import streamlit as st
import webbrowser

st.set_page_config(
    page_title="Acceso Cliente",
    page_icon="🔗",
    layout="centered"
)

st.title("🔗 Acceso al Sistema")

url_param = st.experimental_get_query_params().get("url", [""])[0]

if url_param:
    if st.button("🚀 Acceder al Sistema de Gestión", use_container_width=True):
        webbrowser.open_new_tab(url_param)
    st.markdown(f"*URL de destino:* `{url_param}`")
else:
    st.warning("No se ha configurado la URL de destino")
    custom_url = st.text_input("Ingrese la URL manualmente:")
    if custom_url and st.button("🌐 Acceder con URL personalizada", use_container_width=True):
        webbrowser.open_new_tab(custom_url)

st.markdown("---")
st.caption("Sistema de acceso cliente v1.0")