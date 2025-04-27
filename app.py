import streamlit as st
import pandas as pd
import random
from io import BytesIO

# Configura la página
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

# Función para mostrar la página de inicio
def mostrar_inicio():
    st.markdown("<h1 style='text-align: center; font-size: 60px;'>Checkify ✨</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; font-weight: normal;'>Organiza tus eventos de forma elegante y eficiente.<br>Envía códigos únicos, automatiza correos y gestiona la asistencia en segundos.</h3>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("¡Empezar ahora! 🚀", use_container_width=True):
        st.session_state.pagina = 'subir_excel'

# Función para mostrar la carga del Excel
def mostrar_carga_excel():
    st.title("📋 Carga tu lista de invitados")
    st.write("Sube un archivo Excel que tenga dos columnas: `Nombre` y `Correo`.")

    archivo = st.file_uploader("Sube tu archivo (.xlsx)", type=["xlsx"])

    if archivo:
        df = pd.read_excel(archivo)

        if "Nombre" not in df.columns or "Correo" not in df.columns:
            st.error("❌ El archivo debe tener las columnas 'Nombre' y 'Correo'.")
        else:
            # Generar códigos únicos de 4 dígitos
            codigos_usados = set()

            def generar_codigo():
                while True:
                    codigo = f"{random.randint(0, 9999):04}"
                    if codigo not in codigos_usados:
                        codigos_usados.add(codigo)
                        return codigo

            df["Código"] = df.apply(lambda _: generar_codigo(), axis=1)
            df["Asistencia"] = ""  # Columna vacía inicialmente

            st.success("✅ Archivo procesado exitosamente. ¡Tus códigos y campo de asistencia han sido generados!")

            # Mostrar preview
            st.dataframe(df)

            # Guardar en sesión
            st.session_state.df_invitados = df

            # Botón para descargar el Excel modificado
            output = BytesIO()
            df.to_excel(output, index=False)
            st.download_button(
                label="📥 Descargar Excel con Códigos",
                data=output.getvalue(),
                file_name="Invitados_con_codigos.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            if st.button("Continuar ➡️", use_container_width=True):
                st.session_state.pagina = 'crear_correo'

# Función vacía para la siguiente fase
def mostrar_crear_correo():
    st.title("✉️ Crear correo")
    st.write("Esta sección estará disponible en el próximo paso.")

# Lógica de navegación
if st.session_state.pagina == 'inicio':
    mostrar_inicio()
elif st.session_state.pagina == 'subir_excel':
    mostrar_carga_excel()
elif st.session_state.pagina == 'crear_correo':
    mostrar_crear_correo()
