import streamlit as st
import pandas as pd
import random
import json
import gspread
import urllib.parse
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

# Configuración de la página
st.set_page_config(page_title="Checkify - Registro de Asistencia", page_icon="✨", layout="centered")

# CSS bonito
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

# Estado inicial
if 'pagina' not in st.session_state:
    st.session_state.pagina = 'inicio'
if 'texto_correo' not in st.session_state:
    st.session_state.texto_correo = ''
if 'preview_text' not in st.session_state:
    st.session_state.preview_text = ''
if 'evento_creado' not in st.session_state:
    st.session_state.evento_creado = False

# Conexión a Google APIs
creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
gc = gspread.authorize(credentials)
drive_service = build('drive', 'v3', credentials=credentials)

# ID de la carpeta de Drive donde guardarás todos los eventos
CARPETA_ID = "1oYE2ajyHIcj5m7nedFSkw_RW5wUwMgxy"

# EMAIL que tendrá acceso a todos los Sheets creados
USUARIO_COMPARTIR = "checkify.events@gmail.com"

# Funciones

def crear_nueva_hoja(nombre_evento, carpeta_id):
    file_metadata = {
        'name': nombre_evento,
        'mimeType': 'application/vnd.google-apps.spreadsheet',
        'parents': [carpeta_id]
    }
    file = drive_service.files().create(body=file_metadata, fields='id').execute()
    sheet_id = file.get('id')

    # Compartir automáticamente con el usuario
    compartir_hoja_con_usuario(sheet_id, USUARIO_COMPARTIR)

    sheet = gc.open_by_key(sheet_id).sheet1
    return sheet_id, sheet

def compartir_hoja_con_usuario(file_id, email_usuario):
    permission = {
        'type': 'user',
        'role': 'writer',
        'emailAddress': email_usuario
    }
    drive_service.permissions().create(
        fileId=file_id,
        body=permission,
        sendNotificationEmail=False
    ).execute()

def mostrar_inicio():
    st.markdown("<h1 style='text-align: center; font-size: 60px;'>Checkify ✨</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; font-weight: normal;'>Organiza tus eventos de forma elegante y eficiente.<br>Genera códigos únicos, automatiza correos y registra la asistencia en segundos.</h3>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("¡Empezar ahora! 🚀", use_container_width=True):
        st.session_state.pagina = 'subir_excel'

def mostrar_carga_excel():
    st.title("📋 Carga tu lista de invitados")
    st.write("Sube un archivo Excel que contenga dos columnas obligatorias: `Nombre` y `Correo`.")

    nombre_evento = st.text_input("📌 Ingresa el nombre de tu evento")
    archivo = st.file_uploader("Sube tu archivo (.xlsx)", type=["xlsx"])

    if archivo and nombre_evento and not st.session_state.evento_creado:
        with st.spinner('⏳ Cargando tu evento...'):
            df = pd.read_excel(archivo)

            if "Nombre" not in df.columns or "Correo" not in df.columns:
                st.error("❌ El archivo debe tener las columnas 'Nombre' y 'Correo'.")
            else:
                codigos_usados = set()
                def generar_codigo():
                    while True:
                        codigo = f"{random.randint(0, 9999):04}"
                        if codigo not in codigos_usados:
                            codigos_usados.add(codigo)
                            return codigo

                df["Código"] = df.apply(lambda _: generar_codigo(), axis=1)
                df["Asistencia"] = ""

                nuevo_sheet_id, hoja = crear_nueva_hoja(nombre_evento, CARPETA_ID)
                hoja.update([df.columns.values.tolist()] + df.values.tolist())

                st.session_state.sheet_id = nuevo_sheet_id
                st.session_state.evento_creado = True

    if st.session_state.evento_creado:
        st.success("🎉 ¡Evento creado exitosamente!")

        sheet_id_codificado = urllib.parse.quote(st.session_state.sheet_id)
        url_registro = f"https://registrocheckify-pktquohfp88ngbripxot4u.streamlit.app/?sheet_id={sheet_id_codificado}"

        st.markdown(f"🔗 [Haz clic aquí para registrar asistencia de este evento]({url_registro})", unsafe_allow_html=True)

        if st.button("Continuar ➡️", use_container_width=True):
            st.session_state.pagina = 'crear_correo'

def mostrar_crear_correo():
    st.title("✉️ Crear correo personalizado")

    try:
        sheet_id = st.session_state.sheet_id
        sheet = gc.open_by_key(sheet_id).sheet1
        df = pd.DataFrame(sheet.get_all_records())
        columnas = df.columns.tolist()
    except:
        st.error("❌ Error: No se encontró la hoja de invitados. Regresa y crea el evento primero.")
        return

    col1, col2 = st.columns([3, 1])

    with col1:
        texto_correo = st.text_area(
            "✏️ Escribe el correo aquí:",
            value=st.session_state.texto_correo,
            height=400,
            key="area_correo"
        )

    with col2:
        st.markdown("### 📌 Campos disponibles:")
        for col in columnas:
            if st.button(f"Insertar {col}", key=f"boton_{col}"):
                st.session_state.texto_correo += f" {{{col}}} "

    st.session_state.texto_correo = st.session_state.get('area_correo', '')

    if st.button("Guardar plantilla ✅", use_container_width=True):
        st.success("✅ Plantilla de correo guardada correctamente.")
        if not df.empty:
            preview = st.session_state.texto_correo
            primer_invitado = df.iloc[0]
            for col in columnas:
                preview = preview.replace(f"{{{col}}}", str(primer_invitado[col]))
            st.session_state.preview_text = preview

    if st.session_state.preview_text:
        st.markdown("---")
        st.markdown("### 📈 Vista previa del correo:")
        st.write(st.session_state.preview_text)

# Navegación entre páginas
if st.session_state.pagina == 'inicio':
    mostrar_inicio()
elif st.session_state.pagina == 'subir_excel':
    mostrar_carga_excel()
elif st.session_state.pagina == 'crear_correo':
    mostrar_crear_correo()
