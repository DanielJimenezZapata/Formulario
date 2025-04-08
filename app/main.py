import streamlit as st
from admin_view import admin_main
from quota_management import quota_main
from client_quota_view import client_quota_main
from streamlit_option_menu import option_menu

def main():
    # Configuración única de página
    st.set_page_config(
        page_title="Sistema de Gestión de Cupos",
        page_icon="🎫",
        layout="wide",
        initial_sidebar_state="auto"
    )

    # Verificar si es admin para mostrar menú completo
    if st.session_state.get("admin_logged", False):
        with st.sidebar:
            selected = option_menu(
                menu_title="Menú Admin",
                options=["Administración", "Gestión Completa"],
                icons=["shield-lock", "gear"],
                menu_icon="person-lock",
                default_index=0
            )
        
        if selected == "Administración":
            admin_main()
        elif selected == "Gestión Completa":
            quota_main()
    else:
        # Vista cliente normal
        client_quota_main()

if __name__ == "__main__":
    main()