import streamlit as st
from admin_view import admin_main
from quota_management import quota_main
from streamlit_option_menu import option_menu

def main():
    # Configuración única de página
    st.set_page_config(
        page_title="Sistema de Gestión",
        page_icon="📋",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Menú de navegación lateral
    with st.sidebar:
        selected = option_menu(
            menu_title="Menú Principal",
            options=["Administración", "Gestión de Cupos"],
            icons=["shield-lock", "clipboard-data"],
            menu_icon="cast",
            default_index=0
        )

    # Mostrar la página seleccionada
    if selected == "Administración":
        admin_main()
    elif selected == "Gestión de Cupos":
        quota_main()

if __name__ == "__main__":
    main()