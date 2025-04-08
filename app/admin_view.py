import streamlit as st
import time
import pyperclip
from repository.quota_repository import QuotaRepository

def admin_main():
    # Inicialización de variables de sesión
    if "admin_logged" not in st.session_state:
        st.session_state.admin_logged = False
    if "app_urls" not in st.session_state:
        st.session_state.app_urls = {"Principal": "http://localhost:8501"}
    if "selected_url_key" not in st.session_state:
        st.session_state.selected_url_key = list(st.session_state.app_urls.keys())[0]

    st.title("🔐 Panel de Administración")

    # Sistema de login
    if not st.session_state.admin_logged:
        with st.expander("Acceso Administrativo", expanded=True):
            password = st.text_input("Contraseña", type="password")
            if st.button("Ingresar"):
                quota_repo = QuotaRepository()
                if quota_repo.verify_admin_password(password):
                    st.session_state.admin_logged = True
                    st.success("Acceso concedido")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas")
        return

    # Contenido solo para administradores
    quota_repo = QuotaRepository()
    st.success("Sesión administrativa activa")

    # Sección para copiar URL cliente
    st.divider()
    st.header("🔗 Compartir Acceso Cliente")
    
    selected_url = st.session_state.app_urls[st.session_state.selected_url_key]
    client_url = f"{selected_url}/?page=Usar+Cupo"
    
    st.code(client_url, language="text")
    if st.button("📋 Copiar URL para Clientes"):
        try:
            pyperclip.copy(client_url)
            st.success("URL copiada al portapapeles!")
        except:
            st.warning("No se pudo copiar automáticamente. Copia manualmente el texto arriba")

    # Resto del código administrativo...
    # (Mantener las otras secciones de gestión de contraseñas, URLs, etc.)