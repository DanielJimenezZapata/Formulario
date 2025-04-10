import streamlit as st
from urllib.parse import unquote
from repository.quota_repository import QuotaRepository
from storage.url_storage import load_urls

def main():
    st.set_page_config(page_title="Verificación de cupos", page_icon="🔁")

    query_params = st.experimental_get_query_params()
    url_key = query_params.get("url", [None])[0]

    if not url_key:
        st.error("No se especificó una URL.")
        st.stop()
    
    url_key = unquote(url_key)

    st.title(f"📄 {url_key}")

    if "app_urls" not in st.session_state:
        st.session_state.app_urls = load_urls()

    if "app_urls" not in st.session_state:
        st.error("No hay URLs configuradas.")
        st.stop()

    url_data = st.session_state.app_urls.get(url_key)


    if not url_data:
        st.error("La URL especificada no existe.")
        st.stop()

    destino_url = url_data["url"]
    max_cupos = url_data["max_cupos"]

    quota_repo = QuotaRepository()
    inscriptions = quota_repo.get_current_quota_count(url_key)

    st.info(f"Cupos usados: {inscriptions}/{max_cupos}")

    if inscriptions < max_cupos:
        if st.button("🚀 Entrar al formulario"):
            # Incrementar cupo (si lo decides aquí)
            quota_repo.increment_quota_count(url_key)

            st.success("Redireccionando...")
            st.markdown(f"[Haz clic aquí si no redirige automáticamente]({destino_url})")
            st.experimental_set_query_params()
            st.experimental_rerun()
    else:
        st.error("❌ Lo sentimos, no hay cupos disponibles en este momento.")

if __name__ == "__main__":
    main()