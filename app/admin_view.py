import streamlit as st
import time
import pyperclip
from repository.quota_repository import QuotaRepository
from storage.url_storage import load_urls, save_urls
from urllib.parse import quote

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
        st.session_state.app_urls = load_urls()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.expander("➕ Añadir URL"):
            new_name = st.text_input("Nombre descriptivo")
            new_url = st.text_input("URL completa (https://)")
            new_cupos = st.number_input("Máximo de cupos", min_value=0, step=1, key="new_cupos")
            if st.button("Guardar URL"):
                if new_name and new_url:
                    st.session_state.app_urls[new_name] = {
                        "url": new_url,
                        "max_cupos": new_cupos
                    }
                    save_urls(st.session_state.app_urls)
                    
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
    
    with col3:
        with st.expander("📝 Editar URL"):
            if st.session_state.app_urls:
                selected_edit_key = st.selectbox("Seleccionar la URL a editar", options=list(st.session_state.app_urls.keys()))

                url_data = st.session_state.app_urls[selected_edit_key]

                if isinstance(url_data, str):
                    url_data = {"url": url_data, "max_cupos": 0}

                edited_name = st.text_input("Nuevo nombre descriptivo", value=selected_edit_key, key="edit_name")
                edited_url = st.text_input("Nueva URL", value=url_data.get("url", ""), key="edit_url")
                edited_cupos = st.number_input("Máximo de cupos", value=url_data.get("max_cupos", 0), min_value=0, step=1, key="edit_cupos")

            if st.button("Guardar cambios"):
                if edited_name and edited_url:
                    if edited_name != selected_edit_key:
                        st.session_state.app_urls.pop(selected_edit_key)
                    st.session_state.app_urls[edited_name] = {
                        "url": edited_url,
                        "max_cupos": edited_cupos
                    } 
                    st.success("URL actualizada")
                    time.sleep(1)
                    st.rerun()

    # URL principal
    st.divider()
    st.subheader("🌐 URL Principal")
    selected_url = st.selectbox(
        "Selecciona la URL a mostrar",
        options=list(st.session_state.app_urls.keys())
    )
    
    if st.button("📋 Copiar URL de Gestión"):
        url_key_encoded = quote(selected_url)
        quota_url = f"http://localhost:8501/quota_view?url={url_key_encoded}"
        try:
            pyperclip.copy(quota_url)
            st.success("¡URL copiada al portapapeles!")
        except:
            st.code(quota_url)


    # Cerrar sesión
    st.divider()
    if st.button("🚪 Cerrar sesión"):
        st.session_state.clear()
        st.rerun()