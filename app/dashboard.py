import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# luego tus imports normales


# ==============================
# DASHBOARD MATERIA PRIMA
# ==============================

# 1. IMPORTS
import streamlit as st
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
            "threshold": {"line": {"color": "white", "width": 3},
                          "thickness": 0.75, "value": value},
        },
        title={"text": title},
    )).update_layout(template="plotly_dark", height=250,
                     margin=dict(l=20, r=20, t=40, b=20))

# ==============================
# 2. CONFIGURACIÓN
# ==============================

st.set_page_config(
    page_title="Dashboard Materia Prima",
    layout="wide"
)

# ==============================
# 3. TÍTULO
# ==============================

st.title("📦 Dashboard Materia Prima")

# ==============================
# 4. CARGAR DATOS
# ==============================

df_otif = load_query("sql/otif.sql")

df_scorecard = load_query(
    "sql/scorecard_proveedores.sql"
)

df_leadtime = load_query(
    "sql/leadtime.sql"
)

df_fillrate = load_query(
    "sql/fill_rate.sql"
)

# ==============================
# 5. FILTRO PROVEEDOR
# ==============================

with st.sidebar:
    st.title("Filtros")
    proveedor = st.selectbox(
        "Proveedor",
        options=["TODOS"] + list(df_scorecard["Proveedor"].unique())
    )

# ==============================
# 6. FILTRAR DATAFRAMES
# ==============================

if proveedor != "TODOS":

    df_scorecard_filtrado = df_scorecard[
        df_scorecard["Proveedor"] == proveedor
    ]

    df_otif_filtrado = df_otif[
        df_otif["Proveedor"] == proveedor
    ]

    df_leadtime_filtrado = df_leadtime[
        df_leadtime["Proveedor"] == proveedor
    ]

    df_fillrate_filtrado = df_fillrate[
        df_fillrate["Proveedor"] == proveedor
    ]

else:

    df_scorecard_filtrado = df_scorecard

    df_otif_filtrado = df_otif

    df_leadtime_filtrado = df_leadtime

    df_fillrate_filtrado = df_fillrate

# ==============================
# 7. CALCULAR MÉTRICAS
# ==============================

otif = df_otif_filtrado[
    "OTIF_Pct"
].mean()

lead = df_leadtime_filtrado[
    "LeadTime_Promedio"
].mean()

fillrate = df_fillrate_filtrado[
    "Fill_Rate_Pct"
].mean()

# ==============================
# 8. KPIs
# ==============================

c1, c2, c3 = st.columns(3)
c1.plotly_chart(gauge(otif, "OTIF"), use_container_width=True)
c2.plotly_chart(gauge(lead, "Lead Time", max_val=30, suffix=" d", ref=7),
                use_container_width=True)
c3.plotly_chart(gauge(fillrate, "Fill Rate"), use_container_width=True)

# ==============================
# 9. ALERTA OTIF
# ==============================

if otif < 80:

    st.warning(
        "⚠️ OTIF bajo objetivo"
    )

# ==============================
# 10. FUNNEL
# ==============================

data = dict(

    number=[120, 100, 85, 70],

    stage=[
        "Pedidos Solicitados",
        "Pedidos Despachados",
        "Pedidos Recibidos",
        "Pedidos OTIF"
    ]
)

fig_funnel = px.funnel(data, x="number", y="stage",
                       title="Flujo de Abastecimiento")
fig_funnel.update_layout(template="plotly_dark")

df_otif_filtrado = df_otif_filtrado.sort_values("OTIF_Pct")
fig_bar = px.bar(
    df_otif_filtrado, x="Proveedor", y="OTIF_Pct",
    color="OTIF_Pct", color_continuous_scale="RdYlGn",
    range_color=[50, 100], text_auto=".1f",
    title="OTIF por Proveedor",
)
fig_bar.add_hline(y=90, line_dash="dash", line_color="white",
                  annotation_text="Objetivo 90%")
fig_bar.update_layout(template="plotly_dark", hovermode="x unified")

fig_tree = px.treemap(
    df_scorecard_filtrado, path=["Proveedor"], values="Total_OC",
    color="OTIF_Pct", color_continuous_scale="RdYlGn",
    range_color=[50, 100],
    title="Volumen y desempeño por proveedor",
    hover_data=["FillRate_Pct", "LeadTime_Prom_Dias"],
)
fig_tree.update_layout(template="plotly_dark", height=450)

tab1, tab2, tab3 = st.tabs(["Resumen", "OTIF", "Scorecard"])
with tab1:
    st.plotly_chart(fig_funnel, use_container_width=True)
with tab2:
    st.plotly_chart(fig_bar, use_container_width=True)
with tab3:
    st.plotly_chart(fig_tree, use_container_width=True)
    st.dataframe(df_scorecard_filtrado, use_container_width=True)

# ==============================
# 13. EXPORTAR CSV
# ==============================

st.download_button(

    "⬇️ Descargar Scorecard CSV",

    data=df_scorecard_filtrado.to_csv(
        index=False
    ),

    file_name="scorecard_proveedores.csv",

    mime="text/csv"
)

