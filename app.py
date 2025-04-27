import streamlit as st
import pandas as pd
import random

# Configurar página
st.set_page_config(page_title="Checkify - Registro de Asistencia", page_icon="✨", layout="centered")

# Estilos para tipografía y centrado bonito
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

# Estado inicial de navegación
if 'pagina' not in st.session_state:
    st.session_state.pagina = 'inicio'

# Función para mostrar la página de bienvenida
def mostrar_inicio():
    st.markdown("<h1 style='text-align: center; font-size: 60px;'>Checkify ✨</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; font-weight: normal;'>Organiza tus eventos de forma elegante y eficiente.<br> Envía códigos únicos, automatiza correos y gestiona la asistencia en segundos.</h3>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("¡Empezar ahora! 🚀", use_container_width=True):
        st.session_state.pagina = 'subir_excel'

# Función para subir el Excel y generar códigos
def mostrar_carga_excel():
    st.title("📋 Carga tu lista de invitados")
    st.write("Sube un archivo Excel que tenga dos columnas obligatorias: `Nombre` y `Correo`.")

    archivo = st.file_uploader("Sube tu archivo (.xlsx)", type=["xlsx"])

    if archivo:
        df = pd.read_excel(archivo)

        # Verificar que las columnas necesarias existan
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

            st.success("✅ Archivo procesado exitosamente. ¡Tus códigos han sido generados!")

            # Mostrar una vista previa
            st.dataframe(df)

            # Guardarlo en sesión para siguientes pasos
            st.session_state.df_invitados = df

            if st.button("Continuar ➡️", use_container_width=True):
                st.session_state.pagina = 'crear_correo'

# Lógica principal de navegación
if st.session_state.pagina == 'inicio':
    mostrar_inicio()
elif st.session_state.pagina == 'subir_excel':
    mostrar_carga_excel()
elif st.session_state.pagina == 'crear_correo':
    st.title("✏️ Crear el correo")
    st.write("Aquí vamos a elegir si quieres crear el correo manualmente o que lo genere la IA (lo programamos en el siguiente paso).")
