import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

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
    page_title="Proveedores",
    layout="wide"
)

# =========================
# TÍTULO
# =========================

st.title("🏭 Análisis de Proveedores")

# =========================
# CARGAR DATOS
# =========================

df_scorecard = load_query(
    "sql/scorecard_proveedores.sql"
)

df_otif = load_query(
    "sql/otif.sql"
)

df_fill = load_query(
    "sql/fill_rate.sql"
)

df_lead = load_query(
    "sql/leadtime.sql"
)
# Convertir columnas numéricas
df_otif["OTIF_Pct"] = pd.to_numeric(df_otif["OTIF_Pct"], errors="coerce")
df_fill["Fill_Rate_Pct"] = pd.to_numeric(df_fill["Fill_Rate_Pct"], errors="coerce")
df_lead["LeadTime_Promedio"] = pd.to_numeric(df_lead["LeadTime_Promedio"], errors="coerce")
df_scorecard["Total_OC"] = pd.to_numeric(df_scorecard["Total_OC"], errors="coerce")

# =========================
# FILTRO
# =========================

with st.sidebar:
    st.title("Filtros")
    proveedor = st.selectbox(
        "Proveedor",
        options=["TODOS"] + list(df_scorecard["Proveedor"].unique())
    )

# =========================
# FILTRAR DATAFRAMES
# =========================

if proveedor != "TODOS":

    df_scorecard = df_scorecard[
        df_scorecard["Proveedor"] == proveedor
    ]

    df_otif = df_otif[
        df_otif["Proveedor"] == proveedor
    ]

    df_fill = df_fill[
        df_fill["Proveedor"] == proveedor
    ]

    df_lead = df_lead[
        df_lead["Proveedor"] == proveedor
    ]

# =========================
# KPIs
# =========================

otif = df_otif[
    "OTIF_Pct"
].mean()

fillrate = df_fill[
    "Fill_Rate_Pct"
].mean()

leadtime = df_lead[
    "LeadTime_Promedio"
].mean()

total_oc = df_scorecard[
    "Total_OC"
].sum()

# =========================
# KPIs VISUALES
# =========================

c1, c2, c3, c4 = st.columns(4)
c1.plotly_chart(gauge(otif, "OTIF"), use_container_width=True)
c2.plotly_chart(gauge(fillrate, "Fill Rate"), use_container_width=True)
c3.plotly_chart(gauge(leadtime, "Lead Time", max_val=30, suffix=" d", ref=7),
                use_container_width=True)
c4.metric("Total OC", f"{total_oc:,.0f}")

# =========================
# ALERTAS
# =========================

if otif < 80:

    st.error(
        "🚨 Proveedor con OTIF crítico"
    )

elif otif < 90:

    st.warning(
        "⚠️ OTIF bajo objetivo"
    )

else:

    st.success(
        "✅ Buen desempeño OTIF"
    )

# =========================
# SCORE PROVEEDOR
# =========================

df_scorecard["Score"] = (

    df_scorecard["OTIF_Pct"] * 0.4 +

    df_scorecard["FillRate_Pct"] * 0.3 -

    df_scorecard["LeadTime_Prom_Dias"] * 0.3
)

# =========================
# RANKING
# =========================

df_ranking = df_scorecard.sort_values(
    by="Score",
    ascending=False
)

# =========================
# GRÁFICO SCORE
# =========================

fig_score = px.bar(
    df_ranking, x="Proveedor", y="Score",
    color="Score", color_continuous_scale="Viridis",
    text_auto=".1f", title="Ranking Proveedores",
)
fig_score.update_layout(template="plotly_dark", hovermode="x unified")

fig_otif = px.bar(
    df_otif, x="Proveedor", y="OTIF_Pct",
    color="OTIF_Pct", color_continuous_scale="RdYlGn",
    range_color=[50, 100], text_auto=".1f",
    title="OTIF por Proveedor",
)
fig_otif.add_hline(y=90, line_dash="dash", line_color="white",
                   annotation_text="Objetivo 90%")
fig_otif.update_layout(template="plotly_dark", hovermode="x unified")

fig_lead = px.bar(
    df_lead, x="Proveedor", y="LeadTime_Promedio",
    color="LeadTime_Promedio", color_continuous_scale="RdYlGn_r",
    text_auto=".1f", title="Lead Time Promedio (días)",
)
fig_lead.update_layout(template="plotly_dark", hovermode="x unified")

fig_scatter = px.scatter(
    df_scorecard, x="LeadTime_Prom_Dias", y="OTIF_Pct",
    size="Total_OC", color="FillRate_Pct",
    color_continuous_scale="RdYlGn", hover_name="Proveedor",
    title="OTIF vs Lead Time (tamaño = volumen OC)",
)
fig_scatter.update_layout(template="plotly_dark")

tab1, tab2, tab3, tab4 = st.tabs(
    ["Ranking", "OTIF", "Lead Time", "Matriz"]
)
with tab1:
    st.plotly_chart(fig_score, use_container_width=True)
with tab2:
    st.plotly_chart(fig_otif, use_container_width=True)
with tab3:
    st.plotly_chart(fig_lead, use_container_width=True)
with tab4:
    st.plotly_chart(fig_scatter, use_container_width=True)

st.subheader("Scorecard Proveedores")
st.dataframe(df_scorecard, use_container_width=True)

# =========================
# EXPORTAR CSV
# =========================

st.download_button(

    "⬇️ Descargar CSV",

    data=df_scorecard.to_csv(
        index=False
    ),

    file_name="proveedores.csv",

    mime="text/csv"
)

