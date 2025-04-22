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
    query_params = st.query_params.to_dict()  # Nueva forma
    name = query_params.get("name", ["Recurso"])
    target_url = query_params.get("url", ["#"])
    
    # Decodificar parámetros
    name = unquote(name)
    target_url = unquote(target_url)
    
    if target_url == "#":
        st.error("❌ Configuración no proporcionada")
        st.info("Por favor, acceda a través del enlace proporcionado por el administrador")
        return
    
    # Verificar cupos disponibles
    disponibles = quota_repo.get_remaining_slots()
    
    if disponibles <= 0:
        st.error("❌ No hay cupos disponibles")
        st.image("https://cdn-icons-png.flaticon.com/512/179/179386.png", width=100)
        st.info("Por favor, contacte al administrador para más información")
        return
    
    # Mostrar interfaz con cupos disponibles
    st.title(f"Acceso a {name}")
    
    if st.button("▶️ Acceder", type="primary"):
        # Reducir el cupo antes de redirigir
        result = quota_repo.decrement_slot()
        
        if "error" in result:
            st.error(f"Error al reservar cupo: {result['error']}")
        else:
            # Redirigir a la URL destino
            st.markdown(f'<meta http-equiv="refresh" content="0; url={target_url}">', 
                       unsafe_allow_html=True)
    
    st.markdown("---")
    st.caption("Sistema de acceso controlado | Contacte al administrador para asistencia")

if __name__ == "__main__":
    main()