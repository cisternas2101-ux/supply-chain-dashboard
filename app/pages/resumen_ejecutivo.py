import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# luego tus imports normales
import plotly.express as px
from utils.loader import load_query

# =========================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.loader import load_query


def gauge(value, title, max_val=100, suffix="%", ref=90):
    return go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        number={"suffix": suffix},
        delta={"reference": ref},
        gauge={
            "axis": {"range": [0, max_val]},
            "bar": {"color": "#00CC96"},
            "steps": [
                {"range": [0, max_val * 0.6], "color": "#EF553B"},
                {"range": [max_val * 0.6, max_val * 0.8], "color": "#FFA15A"},
                {"range": [max_val * 0.8, max_val], "color": "#19D3F3"},
            ],
        },
        title={"text": title},
    )).update_layout(template="plotly_dark", height=230,
                     margin=dict(l=20, r=20, t=40, b=20))

# =========================
# CONFIG
# =========================

st.set_page_config(
    page_title="Resumen Ejecutivo",
    layout="wide"
)

# =========================
# TÍTULO
# =========================

st.title("📊 Resumen Ejecutivo Supply Chain")

# =========================
# CARGAR DATOS
# =========================

df_scorecard = load_query(
    "sql/scorecard_proveedores.sql"
)

df_semana = load_query(
    "sql/pendiente_por_semana.sql"
)

df_otif = load_query(
    "sql/otif.sql"
)

with st.sidebar:
    st.title("Filtros")
    proveedor = st.selectbox(
        "Proveedor",
        options=["TODOS"] + list(df_scorecard["Proveedor"].unique())
    )

if proveedor != "TODOS":
    df_scorecard = df_scorecard[df_scorecard["Proveedor"] == proveedor]
    df_otif = df_otif[df_otif["Proveedor"] == proveedor]

# =========================
# KPIs GENERALES
# =========================

otif_global = df_scorecard[
    "OTIF_Pct"
].mean()

fill_global = df_scorecard[
    "FillRate_Pct"
].mean()

lead_global = df_scorecard[
    "LeadTime_Prom_Dias"
].mean()

pendientes = df_semana[
    "Pendientes"
].sum()

df_scorecard["OTIF_Pct"] = pd.to_numeric(df_scorecard["OTIF_Pct"], errors="coerce")
df_scorecard["FillRate_Pct"] = pd.to_numeric(df_scorecard["FillRate_Pct"], errors="coerce")
df_scorecard["LeadTime_Prom_Dias"] = pd.to_numeric(df_scorecard["LeadTime_Prom_Dias"], errors="coerce")
df_semana["Pendientes"] = pd.to_numeric(df_semana["Pendientes"], errors="coerce")
# =========================
# KPIs
# =========================

c1, c2, c3, c4 = st.columns(4)
c1.plotly_chart(gauge(otif_global, "OTIF Global"),
                use_container_width=True)
c2.plotly_chart(gauge(fill_global, "Fill Rate"),
                use_container_width=True)
c3.plotly_chart(gauge(lead_global, "Lead Time", max_val=30, suffix=" d", ref=7),
                use_container_width=True)
c4.metric("Pendientes", f"{pendientes:,.0f}")

# =========================
# ALERTAS
# =========================

if otif_global < 80:

    st.error(
        "🚨 Riesgo alto en abastecimiento"
    )

elif otif_global < 90:

    st.warning(
        "⚠️ OTIF bajo objetivo"
    )

else:

    st.success(
        "✅ Operación estable"
    )

# =========================
# TOP PROVEEDORES
# =========================

top = df_scorecard.sort_values(
    by="OTIF_Pct",
    ascending=False
).head(5)

fig_top = px.bar(
    top, x="Proveedor", y="OTIF_Pct",
    color="OTIF_Pct", color_continuous_scale="Greens",
    range_color=[50, 100], text_auto=".1f",
    title="Top 5 OTIF",
)
fig_top.update_layout(template="plotly_dark", hovermode="x unified")

worst = df_scorecard.sort_values("OTIF_Pct").head(5)
fig_worst = px.bar(
    worst, x="Proveedor", y="OTIF_Pct",
    color="OTIF_Pct", color_continuous_scale="Reds_r",
    range_color=[0, 80], text_auto=".1f",
    title="Proveedores Críticos",
)
fig_worst.update_layout(template="plotly_dark", hovermode="x unified")

fig_semana = px.area(
    df_semana, x="Semana", y=["Llegaron", "Pendientes"],
    title="Tendencia Pedidos",
)
fig_semana.update_layout(
    template="plotly_dark", hovermode="x unified",
    xaxis=dict(rangeslider=dict(visible=True)),
)

fig_tree = px.treemap(
    df_scorecard, path=["Proveedor"], values="Total_OC",
    color="OTIF_Pct", color_continuous_scale="RdYlGn",
    range_color=[50, 100],
    title="Mapa de proveedores (volumen y OTIF)",
)
fig_tree.update_layout(template="plotly_dark", height=450)

tab1, tab2, tab3, tab4 = st.tabs(
    ["Top/Críticos", "Tendencia", "Mapa", "Tabla"]
)
with tab1:
    cA, cB = st.columns(2)
    cA.plotly_chart(fig_top, use_container_width=True)
    cB.plotly_chart(fig_worst, use_container_width=True)
with tab2:
    st.plotly_chart(fig_semana, use_container_width=True)
with tab3:
    st.plotly_chart(fig_tree, use_container_width=True)
with tab4:
    st.dataframe(df_scorecard, use_container_width=True)



