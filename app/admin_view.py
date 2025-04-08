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
    if "remaining_slots" not in st.session_state:
        st.session_state.remaining_slots = 100
    if "button_clicked" not in st.session_state:
        st.session_state.button_clicked = False

    st.title("🔧 Panel de Administración")

    # Sistema de login
    if not st.session_state.admin_logged:
        with st.expander("🔐 Admin Login", expanded=True):
            password = st.text_input("Contraseña", type="password", key="admin_pass_input")
            if st.button("Ingresar"):
                quota_repo = QuotaRepository()
                if quota_repo.verify_admin_password(password):
                    st.session_state.admin_logged = True
                    st.success("Login exitoso")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Contraseña incorrecta")
    else:
        st.success("Modo Administrador Activo")
        quota_repo = QuotaRepository()

        # Sección de cambio de contraseña
        st.divider()
        st.header("🔑 Cambiar Contraseña")
        with st.expander("Cambiar contraseña", expanded=False):
            current_pass = st.text_input("Contraseña actual", type="password", key="current_pass_input")
            new_pass = st.text_input("Nueva contraseña", type="password", key="new_pass_input")
            confirm_pass = st.text_input("Confirmar nueva contraseña", type="password", key="confirm_pass_input")

            if st.button("Actualizar contraseña"):
                if not quota_repo.verify_admin_password(current_pass):
                    st.error("Contraseña actual incorrecta")
                elif not new_pass:
                    st.error("La nueva contraseña no puede estar vacía")
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

        with st.expander("➕ Añadir URL", expanded=False):
            new_name = st.text_input("Nombre descriptivo", key="new_url_name")
            new_url = st.text_input("URL completa (https://)", key="new_url_value")
            if st.button("Guardar URL"):
                if new_name and new_url:
                    if new_name in st.session_state.app_urls:
                        st.error("Ya existe una URL con ese nombre")
                    else:
                        st.session_state.app_urls[new_name] = new_url
                        st.success(f"URL '{new_name}' añadida")
                        time.sleep(1)
                        st.rerun()
                else:
                    st.error("Debes completar ambos campos")

        with st.expander("➖ Eliminar URL", expanded=False):
            if len(st.session_state.app_urls) > 1:
                url_to_delete = st.selectbox(
                    "Selecciona URL a eliminar",
                    options=[k for k in st.session_state.app_urls.keys() if k != st.session_state.selected_url_key],
                    key="url_to_delete"
                )
                if st.button("Confirmar eliminación"):
                    del st.session_state.app_urls[url_to_delete]
                    st.success(f"URL '{url_to_delete}' eliminada")
                    time.sleep(1)
                    st.rerun()
            else:
                st.warning("Debe haber al menos una URL en el sistema")

        # URL principal y botón de copiar
        st.subheader("🌐 URL Principal")
        st.session_state.selected_url_key = st.selectbox(
            "Selecciona la URL a mostrar",
            options=list(st.session_state.app_urls.keys()),
            key="url_selector"
        )
        
        if st.button("📋 Copiar URL de Gestión de Cupos"):
            selected_url = st.session_state.app_urls[st.session_state.selected_url_key]
            quota_url = f"{selected_url}/?page=Gestión+de+Cupos"
            try:
                pyperclip.copy(quota_url)
                st.success("¡URL copiada al portapapeles!")
                st.code(quota_url, language="text")
            except:
                st.warning("No se pudo copiar al portapapeles. Copia manualmente:")
                st.code(quota_url, language="text")

        # Gestión de cupos
        st.divider()
        st.header("🎫 Gestión de Cupos")
        if st.button("🔄 Resetear cupos a 100"):
            result = quota_repo.reset_slots()
            if "error" in result:
                st.error(result["error"])
            else:
                st.session_state.remaining_slots = 100
                st.session_state.button_clicked = False
                st.success("Cupos reseteados correctamente")
                time.sleep(1)
                st.rerun()

        # Cerrar sesión
        st.divider()
        if st.button("🚪 Cerrar sesión"):
            st.session_state.admin_logged = False
            st.rerun()