import streamlit as st
from repository.quota_repository import QuotaRepository
from admin_view import check_authentication

def quota_main():
    st.title("📊 Gestión de Cupos")
    quota_repo = QuotaRepository()

    # Mostrar métricas
    remaining = quota_repo.get_remaining_slots()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Cupos disponibles", remaining)
    with col2:
        st.metric("Cupos usados", 100 - remaining)
    
    st.progress(remaining/100)

    # Opciones de gestión
    st.divider()
    st.header("🛠️ Opciones de gestión")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Resetear a 100"):
            if quota_repo.reset_slots():
                st.success("Cupos reseteados")
                st.rerun()
    
    with col2:
        if st.button("➖ Reducir cupo"):
            result = quota_repo.decrement_slot()
            if "error" in result:
                st.error(result["error"])
            else:
                st.success("Cupo reducido")
                st.rerun()

    # Ajuste manual
    st.divider()
    new_value = st.number_input(
        "Establecer nuevo valor total",
        min_value=1,
        max_value=1000,
        value=100
    )
    
    if st.button("💾 Guardar cambios"):
        if quota_repo.reset_slots(new_value):
            st.success(f"Cupos actualizados a {new_value}")
            st.rerun()

    st.divider()
    st.info("ℹ️ Los cupos se actualizan en tiempo real")