import streamlit as st
from repository.quota_repository import QuotaRepository
from admin_view import check_authentication

def use_quota_main():
    st.title("🎟️ Usar Cupo")
    quota_repo = QuotaRepository()
    
    # Mostrar disponibilidad
    disponibles = quota_repo.get_remaining_slots()
    
    if disponibles <= 0:
        st.error("❌ No hay cupos disponibles")
        st.image("https://cdn-icons-png.flaticon.com/512/179/179386.png", width=100)
    else:
        st.success(f"✅ Hay {disponibles} cupos disponibles")
        
        if st.button("🚀 Usar mi Cupo", type="primary"):
            result = quota_repo.decrement_slot()
            if "error" in result:
                st.error(f"❌ {result['error']}")
            else:
                st.balloons()
                st.success("🎉 Cupo utilizado exitosamente!")
                
                # Redireccionar a la URL principal configurada
                if "app_urls" in st.session_state and st.session_state.app_urls:
                    main_url = list(st.session_state.app_urls.values())[0]
                    st.markdown(f"🔗 [Ir al sitio principal]({main_url})", unsafe_allow_html=True)
    
    st.markdown("---")
    st.caption("Sistema de gestión v2.0 | © 2025")