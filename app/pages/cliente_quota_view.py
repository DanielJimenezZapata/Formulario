import streamlit as st
from repository.quota_repository import QuotaRepository

def client_quota_main():  # Nombre corregido
    # Configuración de vista cliente
    st.set_page_config(
        page_title="Registro de Cupos",
        page_icon="🎟️",
        layout="centered"
    )

    st.title("🎟️ Registro de Cupo")
    quota_repo = QuotaRepository()
    
    # Mostrar disponibilidad
    disponibles = quota_repo.get_remaining_slots()
    
    if disponibles <= 0:
        st.error("No hay cupos disponibles")
        st.image("https://cdn-icons-png.flaticon.com/512/179/179386.png", width=100)
    else:
        st.success(f"Cupos disponibles: {disponibles}")
        st.progress(disponibles/100)
        
        # Formulario de registro
        with st.form("registro"):
            nombre = st.text_input("Nombre completo*")
            email = st.text_input("Email*")
            
            if st.form_submit_button("📝 Registrar mi cupo"):
                if not all([nombre, email]):
                    st.warning("Complete todos los campos")
                else:
                    result = quota_repo.decrement_slot()
                    if "error" in result:
                        st.error(result["error"])
                    else:
                        st.balloons()
                        st.success(f"Registro exitoso para {nombre}")
                        st.rerun()
    
    st.markdown("---")
    st.caption("Sistema de gestión v2.0")