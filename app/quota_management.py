import streamlit as st
import time
from quota_repository import QuotaRepository

def quota_main():
    st.title("📊 Gestión Avanzada de Cupos")
    quota_repo = QuotaRepository()
    
    # --- Selector de Recursos ---
    st.divider()
    st.header("🔍 Selección de Recurso")
    
    all_urls = quota_repo.get_all_urls()
    if not all_urls:
        st.warning("No hay URLs registradas. Agrega recursos en el panel de Administración.")
        return
    
    selected_url = st.selectbox(
        "Seleccionar recurso para gestionar cupos",
        options=list(all_urls.keys()),
        key="url_selector_quota"
    )
    
    # --- Panel de Control ---
    st.divider()
    st.header("🎛️ Panel de Control")
    
    quota_info = quota_repo.get_url_quota(selected_url)
    
    # Columnas
    col1, col2 = st.columns(2)
    
    # Métricas (Tasa de uso, Cupos disponibles, Ultimo Reset)
    col1.metric(
        "Cupos Disponibles", 
        f"{quota_info['remaining_quota']}/{quota_info['max_quota']}",
        delta=f"{quota_info['remaining_quota'] - quota_info['max_quota']} diferencia"
    )
    
    col2.metric(
        "Tasa de Uso", 
        f"{(1 - (quota_info['remaining_quota'] / quota_info['max_quota'])) * 100:.1f}%"
    )
    
    
    st.progress(quota_info['remaining_quota'] / quota_info['max_quota'])
    
    # --- Acciones de Gestión ---
    st.divider()
    st.header("⚙️ Acciones")
    
    with st.expander("🔧 Configuración Avanzada", expanded=True):
        new_quota = st.number_input(
            "Nuevo cupo máximo",
            min_value=1,
            max_value=1000,
            value=quota_info['max_quota'],
            key=f"max_quota_{selected_url}"
        )
        
        if st.button("🔄 Resetear cupos", key=f"reset_{selected_url}"):
            with st.spinner("Actualizando cupos..."):
                if quota_repo.reset_url_quota(selected_url, int(new_quota)):
                    st.toast(f"✅ Cupos reseteados a {new_quota} para {selected_url}", icon="✅")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ No se pudo actualizar. Verifica la consola para más detalles.")
    
    # --- Resumen General ---
    st.divider()
    if st.checkbox("Mostrar resumen de todos los recursos"):
        all_quotas = quota_repo.get_all_quotas()
        if all_quotas:
            st.subheader("📋 Estado Actual de Todos los Recursos")
            for url, data in all_quotas.items():
                st.info(f"**{url}**: {data['remaining_quota']}/{data['max_quota']} cupos")