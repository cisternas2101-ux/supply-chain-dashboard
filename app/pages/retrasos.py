import streamlit as st
import plotly.express as px

from utils.loader import load_query

# =========================
# CONFIG
# =========================

st.set_page_config(
    page_title="Retrasos",
    layout="wide"
)

# =========================
# TÍTULO
# =========================

st.title("⏰ Análisis de Retrasos")

# =========================
# CARGAR DATOS
# =========================

df_motivo = load_query(
    "sql/motivo_retraso.sql"
)

df_prom = load_query(
    "sql/dia_prom_retraso.sql"
)

# =========================
# PIE CHART
# =========================

fig_pie = px.sunburst(
    df_motivo, path=["Motivo"], values="Frecuencia",
    color="Frecuencia", color_continuous_scale="Reds",
    title="Motivos de Retraso",
)
fig_pie.update_layout(template="plotly_dark", height=450)

fig_bar = px.bar(
    df_prom.sort_values("Dias_Retraso_Prom", ascending=False),
    x="Motivo", y="Dias_Retraso_Prom",
    color="Dias_Retraso_Prom", color_continuous_scale="RdYlGn_r",
    text_auto=".1f", title="Días Promedio de Retraso",
)
fig_bar.update_layout(template="plotly_dark", hovermode="x unified")

tab1, tab2, tab3 = st.tabs(["Distribución", "Días promedio", "Tabla"])
with tab1:
    st.plotly_chart(fig_pie, use_container_width=True)
with tab2:
    st.plotly_chart(fig_bar, use_container_width=True)
with tab3:
    st.dataframe(df_prom, use_container_width=True)

