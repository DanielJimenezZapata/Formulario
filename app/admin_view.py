import streamlit as st
import time
import pyperclip
from repository.quota_repository import QuotaRepository

def check_authentication():
    """Verifica si el usuario está autenticado"""
    if "admin_logged" not in st.session_state:
        st.session_state.admin_logged = False
    
    if not st.session_state.admin_logged:
        show_login()
        return False
    return True

def show_login():
    """Muestra el formulario de login"""
    st.title("🔒 Acceso Administrativo")
    with st.form("login_form"):
        password = st.text_input("Contraseña", type="password")
        submit_button = st.form_submit_button("Ingresar")
        
        if submit_button:
            quota_repo = QuotaRepository()
            if quota_repo.verify_admin_password(password):
                st.session_state.admin_logged = True
                st.success("Login exitoso")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Contraseña incorrecta")
    st.stop()

def admin_main():
    st.title("🔧 Panel de Administración")
    quota_repo = QuotaRepository()

    # Sección de cambio de contraseña
    st.divider()
    with st.expander("🔑 Cambiar Contraseña", expanded=True):
        current_pass = st.text_input("Contraseña actual", type="password")
        new_pass = st.text_input("Nueva contraseña", type="password")
        confirm_pass = st.text_input("Confirmar nueva contraseña", type="password")

        if st.button("Actualizar contraseña"):
            if not quota_repo.verify_admin_password(current_pass):
                st.error("Contraseña actual incorrecta")
            elif new_pass != confirm_pass:
                st.error("Las contraseñas no coinciden")
            else:
                if quota_repo.update_admin_password(new_pass):
                    st.success("Contraseña actualizada exitosamente")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Error al actualizar la contraseña")

    # Gestión de URLs
    st.divider()
    st.header("📌 Gestión de URLs")
    
    if "app_urls" not in st.session_state:
        st.session_state.app_urls = {"Principal": "http://localhost:8501"}
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.expander("➕ Añadir URL"):
            new_name = st.text_input("Nombre descriptivo")
            new_url = st.text_input("URL completa (https://)")
            if st.button("Guardar URL"):
                if new_name and new_url:
                    st.session_state.app_urls[new_name] = new_url
                    st.success("URL añadida")
                    time.sleep(1)
                    st.rerun()

    with col2:
        with st.expander("➖ Eliminar URL"):
            if len(st.session_state.app_urls) > 1:
                url_to_delete = st.selectbox(
                    "Selecciona URL a eliminar",
                    options=list(st.session_state.app_urls.keys())[1:]
                )
                if st.button("Confirmar eliminación"):
                    del st.session_state.app_urls[url_to_delete]
                    st.success("URL eliminada")
                    time.sleep(1)
                    st.rerun()
            else:
                st.warning("Debe haber al menos una URL")

    # URL principal
    st.divider()
    st.subheader("🌐 URL Principal")
    selected_url = st.selectbox(
        "Selecciona la URL a mostrar",
        options=list(st.session_state.app_urls.keys())
    )
    
    if st.button("📋 Copiar URL de Gestión"):
        quota_url = f"{st.session_state.app_urls[selected_url]}/?page=Gestión+de+Cupos"
        try:
            pyperclip.copy(quota_url)
            st.success("¡URL copiada al portapapeles!")
        except:
            st.code(quota_url)

    # Gestión de cupos
    st.divider()
    if st.button("🔄 Resetear cupos a 100"):
        if quota_repo.reset_slots():
            st.success("Cupos reseteados")
            time.sleep(1)
            st.rerun()

    # Cerrar sesión
    st.divider()
    if st.button("🚪 Cerrar sesión"):
        st.session_state.clear()
        st.rerun()