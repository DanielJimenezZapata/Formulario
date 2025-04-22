import streamlit as st
from urllib.parse import parse_qs, unquote
from quota_repository import QuotaRepository

def main():
    st.set_page_config(
        page_title="Acceso Cliente",
        page_icon="👉",
        layout="centered"
    )
    
    quota_repo = QuotaRepository()
    
    # Obtener parámetros de la URL
    query_params = st.query_params.to_dict()
    url_name = unquote(query_params.get("name", "Recurso"))
    target_url = unquote(query_params.get("url", "#"))
    
    if target_url == "#":
        st.error("❌ Configuración no proporcionada")
        return
    
    # Verificar cupos específicos para esta URL
    quota_repo = QuotaRepository()
    print(f"Consultando cupos para: {url_name}")  # Verifica en la terminal
    quota_info = quota_repo.get_url_quota(url_name)
    print(f"Resultado de BD: {quota_info}")  # Debe mostrar {'remaining_quota': 100, ...}
    
    if quota_info['remaining_quota'] <= 0:
        st.error("❌ No hay cupos disponibles para este recurso")
        return
    
    st.title(f"Acceso a {url_name}")
    
    if st.button("▶️ Acceder", type="primary"):
        result = quota_repo.decrement_url_quota(url_name)
        if "error" in result:
            st.error(f"Error: {result['error']}")
        else:
            st.markdown(f'<meta http-equiv="refresh" content="0; url={target_url}">', 
                       unsafe_allow_html=True)
    
    st.markdown("---")
    st.caption(f"Cupos específicos para este recurso | Último reset: {quota_info.get('last_reset', 'N/A')}")
if __name__ == "__main__":
    main()