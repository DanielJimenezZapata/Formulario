import streamlit as st
import time
import pyperclip
import re
from quota_repository import QuotaRepository
from urllib.parse import quote

def check_authentication():
    if "admin_logged" not in st.session_state:
        st.session_state.admin_logged = False
    
    if not st.session_state.admin_logged:
        show_login()
        return False
    return True

def show_login():
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

def is_valid_url(url):
    regex = re.compile(
        r'^(https?://)'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ip
        r'(?::\d+)?'  # port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None

def generate_client_url(name, url, client_port=8502):
    encoded_config = f"name={quote(name)}&url={quote(url)}"
    return f"http://10.33.17.161:{client_port}/?{encoded_config}"

def admin_main():
    st.title("🔧 Panel de Administración")
    quota_repo = QuotaRepository()
    
    # Cargar URLs desde la base de datos
    if "app_urls" not in st.session_state:
        st.session_state.app_urls = quota_repo.get_all_urls()
        if not st.session_state.app_urls:  # Si está vacío, añadir default
            default_url = "http://localhost:8501"
            quota_repo.save_url("Principal", default_url)
            st.session_state.app_urls = {"Principal": default_url}

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
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.expander("➕ Añadir URL"):
            new_name = st.text_input("Nombre descriptivo", key="new_url_name")
            new_url = st.text_input("URL completa (https://)", key="new_url_value")
            if st.button("Guardar URL"):
                if not new_name or not new_url:
                    st.warning("Complete todos los campos")
                elif not is_valid_url(new_url):
                    st.error("URL no válida. Debe comenzar con http:// o https://")
                else:
                    if quota_repo.save_url(new_name, new_url):
                        st.session_state.app_urls = quota_repo.get_all_urls()
                        st.success("URL añadida")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Error al guardar en la base de datos")
    with col2:
        with st.expander("✏️ Editar URL", expanded=True):
            if st.session_state.app_urls:
                url_to_edit = st.selectbox(
                    "Selecciona URL a editar",
                    options=list(st.session_state.app_urls.keys()),
                    key="url_to_edit"
                )
                
                new_name = st.text_input(
                    "Nuevo nombre",
                    value=url_to_edit,
                    key="new_url_name_edit"
                )
                
                new_url = st.text_input(
                    "Nueva URL",
                    value=st.session_state.app_urls[url_to_edit],
                    key="new_url_value_edit"
                )
                
                if st.button("💾 Guardar cambios", key="save_edit"):
                    if not new_name or not new_url:
                        st.warning("Complete todos los campos")
                    elif not is_valid_url(new_url):
                        st.error("URL no válida. Debe comenzar con http:// o https://")
                    elif new_name != url_to_edit and new_name in st.session_state.app_urls:
                        st.error("Ya existe una URL con ese nombre")
                    else:
                        if quota_repo.update_url(url_to_edit, new_name, new_url):
                            st.session_state.app_urls = quota_repo.get_all_urls()
                            st.success("URL actualizada")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Error al actualizar en la base de datos")
    with col3:
        with st.expander("➖ Eliminar URL"):
            if len(st.session_state.app_urls) > 1:
                url_to_delete = st.selectbox(
                    "Selecciona URL a eliminar",
                    options=list(st.session_state.app_urls.keys())[1:],
                    key="url_to_delete"
                )
                if st.button("Confirmar eliminación"):
                    if quota_repo.delete_url(url_to_delete):
                        st.session_state.app_urls = quota_repo.get_all_urls()
                        st.success("URL eliminada")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Error al eliminar de la base de datos")
            else:
                st.warning("Debe haber al menos una URL")

    # Generación de URLs para clientes
    st.divider()
    st.header("👥 Acceso para Clientes")
    
    selected_client_url = st.selectbox(
        "Seleccione recurso para compartir",
        options=list(st.session_state.app_urls.keys()),
        key="selected_client_url"
    )
    
    client_port = st.number_input(
        "Puerto de la app cliente", 
        value=8502, 
        min_value=8000, 
        max_value=9000,
        key="client_port"
    )
    
    if st.button("🖇 Generar Enlace Cliente"):
        client_url = generate_client_url(
            selected_client_url,
            st.session_state.app_urls[selected_client_url],
            client_port
        )
        try:
            pyperclip.copy(client_url)
            st.success("¡Enlace copiado al portapapeles!")
            st.code(client_url)
        except:
            st.error("Error al copiar al portapapeles")
            st.code(client_url)

    

    # Cerrar sesión
    st.divider()
    if st.button("🚪 Cerrar sesión"):
        st.session_state.clear()
        st.rerun()