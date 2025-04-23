import streamlit as st
from admin_view import admin_main, check_authentication
from quota_management import quota_main
from streamlit_option_menu import option_menu

def main():
    st.set_page_config(
        page_title="Sistema de Gestión",
        page_icon="📋",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    if not check_authentication():
        return

    with st.sidebar:
        selected = option_menu(
            menu_title="Menú Principal",
            options=["Administración", "Gestión de Cupos"],
            icons=["shield-lock", "clipboard-data", "person-plus"],
            menu_icon="cast",
            default_index=0
        )

    if selected == "Administración":
        admin_main()
    elif selected == "Gestión de Cupos":
        quota_main()
    

if __name__ == "__main__":
    main()