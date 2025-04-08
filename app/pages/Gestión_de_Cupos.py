import streamlit as st
from repository.quota_repository import QuotaRepository

st.title("🎫 Gestión de Cupos")

quota_repo = QuotaRepository()

# Show available slots
remaining_slots = quota_repo.get_remaining_slots()
if remaining_slots == -1:
    st.error("Error al conectar con la base de datos")
else:
    st.metric("Cupos Disponibles", remaining_slots)

col1, col2 = st.columns(2)

with col1:
    if st.button("Usar un cupo"):
        result = quota_repo.decrement_slot()
        if "error" in result:
            st.error(result["error"])
        else:
            st.success(result["message"])
            st.rerun()

with col2:
    if st.button("Resetear cupos a 100"):
        result = quota_repo.reset_slots()
        if "error" in result:
            st.error(result["error"])
        else:
            st.success(result["message"])
            st.rerun()

st.divider()
st.info("Esta es la vista de gestión de cupos. Puedes usar los botones para controlar la disponibilidad.")