import streamlit as st
from repository.quota_repository import QuotaRepository

def quota_main():
    st.title("📊 Gestión de Cupos")
    quota_repo = QuotaRepository()

    # Mostrar métricas
    remaining_slots = quota_repo.get_remaining_slots()
    
    if remaining_slots == -1:
        st.error("Error al conectar con la base de datos")
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Cupos disponibles", remaining_slots)
        with col2:
            st.metric("Cupos usados", 100 - remaining_slots)

        st.progress(remaining_slots/100)

    # Opciones de gestión
    st.divider()
    st.header("🛠️ Opciones de gestión")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Resetear cupos a 100"):
            result = quota_repo.reset_slots()
            if "error" in result:
                st.error(result["error"])
            else:
                st.success("Cupos reseteados exitosamente")
                st.rerun()
    
    with col2:
        if st.button("➖ Reducir cupo disponible"):
            result = quota_repo.decrement_slot()
            if "error" in result:
                st.error(result["error"])
            else:
                st.success("Cupo reducido exitosamente")
                st.rerun()

    # Ajuste manual
    st.divider()
    st.header("🔢 Ajuste manual")
    
    new_value = st.number_input(
        "Establecer nuevo valor de cupos totales",
        min_value=1,
        max_value=1000,
        value=100,
        step=1
    )
    
    if st.button("💾 Guardar cambios manuales"):
        result = quota_repo.reset_slots(new_value)
        if "error" in result:
            st.error(result["error"])
        else:
            st.success(f"Cupos actualizados a {new_value}")
            st.rerun()

    st.divider()
    st.info("ℹ️ Los cupos se actualizan en tiempo real para todos los usuarios")