import streamlit as st
import time
import pyperclip
import re
from quota_repository import QuotaRepository
from urllib.parse import quote
from dotenv import load_dotenv
import os

def get_client_ip():
    """Obtiene la IP real del cliente"""
    import socket
    try:
        hostname = socket.gethostname()
        return socket.gethostbyname(hostname)
    except:
        return "127.0.0.1"  # Fallback para localhost


def check_authentication():
    if "admin_logged" not in st.session_state:
        st.session_state.admin_logged = False
    
    quota_repo = QuotaRepository()
    client_ip = get_client_ip()
    
    # Verificar si la IP está bloqueada
    blocked_until = quota_repo.is_ip_blocked(client_ip)
    if blocked_until:
        print(f"🚨 [BLOQUEO ACTIVO] IP: {client_ip} | Bloqueado hasta: {blocked_until}")
        st.error(f"🔒 Acceso bloqueado. Intenta nuevamente después de {blocked_until}")
        st.stop()
    
    if not st.session_state.admin_logged:
        show_login(quota_repo, client_ip)
        return False
    return True

def show_login(quota_repo, client_ip):
    st.title("🔒 Acceso Administrativo")
    with st.form("login_form"):
        password = st.text_input("Contraseña", type="password")
        submit_button = st.form_submit_button("Ingresar")
        
        if submit_button:
            print(f"🔑 [INTENTO LOGIN] IP: {client_ip} | Hora: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            if quota_repo.verify_admin_password(password):
                st.session_state.admin_logged = True
                print(f"✅ [LOGIN EXITOSO] IP: {client_ip}")
                st.success("Login exitoso")
                time.sleep(1)
                st.rerun()
            else:
                # Registrar intento fallido
                attempts = quota_repo.record_failed_attempt(client_ip)
                print(f"❌ [LOGIN FALLIDO] IP: {client_ip} | Intentos: {attempts}")
                st.error("Contraseña incorrecta")
                # Verificar si ahora está bloqueado
                if quota_repo.is_ip_blocked(client_ip):
                    print(f"🚨 [IP BLOQUEADA] IP: {client_ip} | Bloqueado por 3 minutos")
                    st.error("Demasiados intentos fallidos. Acceso bloqueado por 3 minutos.")
                    time.sleep(1)
                    st.rerun()


def is_valid_url(url):
    regex = re.compile(
        r'^(https?://)'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ip
        r'(?::\d+)?'  # port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None

load_dotenv()
def generate_client_url(name, url):
    client_port = os.getenv('CLIENT_PORT', '8501')  # Default 8501
    encoded_config = f"name={quote(name)}&url={quote(url)}"
    return f"http://10.33.17.161:{client_port}/?{encoded_config}"

def admin_main():
    st.title("🔧 Panel de Administración")
    quota_repo = QuotaRepository()
    
    # Cargar URLs desde la base de datos
    if "app_urls" not in st.session_state:
        st.session_state.app_urls = quota_repo.get_all_urls()
        

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
            try:
                url_to_edit = st.selectbox(
                    "Selecciona URL a editar",
                    options=list(st.session_state.app_urls.keys()),
                    key="edit_url_selector"
                )
                current_url = st.session_state.app_urls[url_to_edit]
            
                new_name = st.text_input(
                    "Nuevo nombre descriptivo",
                    value=url_to_edit,
                    key=f"new_name_{url_to_edit}"
                )
                
                new_url = st.text_input(
                    "Nueva URL completa (https://)",
                    value=current_url,
                    key=f"new_url_{url_to_edit}"
                )
                
                if st.button("💾 Guardar Cambios", key=f"save_btn_{url_to_edit}"):
                    if not new_name or not new_url:
                        st.warning("⚠️ Complete todos los campos")
                    elif not is_valid_url(new_url):
                        st.error("❌ URL no válida. Debe comenzar con http:// o https://")
                    else:
                        try:
                            if quota_repo.update_url(url_to_edit, new_name, new_url):
                                st.session_state.app_urls = quota_repo.get_all_urls()
                                st.success("✅ URL actualizada correctamente")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.warning("ℹ️ No se realizaron cambios (¿los datos son iguales o ya existen?)")
                        except Exception as e:
                            st.error(f"❌ Error crítico: {str(e)}")
                            st.code(str(e))  # Mostrar detalles técnicos
            except (KeyError, AttributeError):
                st.info("ℹ️ No hay URLs disponibles para editar")
    with col3:
        with st.expander("➖ Eliminar URL", expanded=True):
            # Obtener lista de URLs que se pueden eliminar (excluyendo Principal)
            available_urls = list(st.session_state.app_urls.keys())
            deletable_urls = [name for name in available_urls if name != "Principal"]
            
            if not deletable_urls:
                st.warning("No hay URLs adicionales para eliminar")
            else:
                # Definir url_to_delete antes de usarla
                url_to_delete = st.selectbox(
                    "Selecciona URL a eliminar",
                    options=deletable_urls,
                    key="url_to_delete"
                )
                
                if st.button("Confirmar eliminación", key="confirm_delete"):
                    if quota_repo.delete_url(url_to_delete):  # Ahora url_to_delete está definida
                        st.session_state.app_urls = quota_repo.get_all_urls()
                        st.success(f"URL '{url_to_delete}' eliminada correctamente")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Error al eliminar de la base de datos")

    # Generación de URLs para clientes
    st.divider()
    st.header("👥 Acceso para Clientes")
    
    selected_client_url = st.selectbox(
        "Seleccione recurso para compartir",
        options=list(st.session_state.app_urls.keys()),
        key="selected_client_url"
    )
    
    
    
    if st.button("🖇 Generar Enlace Cliente"):
        try:
            client_url = generate_client_url(
                selected_client_url,
                st.session_state.app_urls[selected_client_url]
            )
            try:
                pyperclip.copy(client_url)
                st.success("¡Enlace copiado al portapapeles!")
                st.code(client_url)
            except:
                st.error("Error al copiar al portapapeles")
                st.code(client_url)
        except (KeyError, AttributeError):
                st.info("No puedes generar URL")

    
    
    # Cerrar sesión
    st.divider()
    if st.button("🚪 Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

