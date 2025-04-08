import streamlit as st
from repository.quota_repository import QuotaRepository

def client_quota_main():
    # Configuración específica para clientes
    st.set_page_config(
        page_title="Usar Cupo - Sistema de Gestión",
        page_icon="🎟️",
        layout="centered"
    )

    st.title("🎟️ Usar Cupo Disponible")
    quota_repo = QuotaRepository()
    
    # Obtener y mostrar cupos
    remaining = quota_repo.get_remaining_slots()
    
    if remaining == -1:
        st.error("⚠️ Sistema no disponible temporalmente")
    elif remaining <= 0:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.error("No hay cupos disponibles actualmente")
            st.info("Por favor intente más tarde")
        with col2:
            st.image("https://cdn-icons-png.flaticon.com/512/179/179386.png", width=100)
    else:
        st.success(f"Cupos disponibles: {remaining}")
        st.progress(remaining/100)
        
        # Sección para usar cupo
        st.divider()
        st.subheader("Registrar cupo")
        
        user_email = st.text_input("Ingrese su email:")
        if st.button("✅ Usar cupo ahora", type="primary"):
            if not user_email:
                st.warning("Por favor ingrese su email")
            else:
                result = quota_repo.decrement_slot()
                if "error" in result:
                    st.error(result["error"])
                else:
                    # Registrar el email (necesitarías implementar esta función)
                    st.balloons()
                    st.success(f"Cupo registrado para {user_email}")
                    st.rerun()
        
        st.markdown("---")
        st.caption("Sistema de gestión de cupos v2.0 - Solo uso de cupos")