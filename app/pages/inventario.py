import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# luego tus imports normales
import plotly.express as px
from utils.loader import load_query
# =========================
import streamlit as st
import plotly.express as px
import pandas as pd

from utils.loader import load_query

# =========================
# CONFIG
# =========================

st.set_page_config(
    page_title="Inventario",
    layout="wide"
)

# =========================
# TÍTULO
# =========================

st.title("📦 Inventario y Abastecimiento")

# =========================
# CARGAR DATOS
# =========================

df_semana = load_query(
    "sql/pendiente_por_semana.sql"
)

df = load_query(
    "sql/detalle.sql"
    
)

df["Fecha_Llegada"] = pd.to_datetime(
    df["Fecha_Llegada"]
)

df_area = load_query(
    "sql/pendiente_por_area.sql"
)

with st.sidebar:
    st.title("Filtros")
    proveedor = st.selectbox(
        "Proveedor",
        options=["TODOS"] + list(df["Proveedor"].unique())
    )

if proveedor != "TODOS":
    df = df[df["Proveedor"] == proveedor]

df["Cantidad_Solicitada"] = pd.to_numeric(
    df["Cantidad_Solicitada"],
    errors="coerce"
)

df["Cantidad_llegada"] = pd.to_numeric(
    df["Cantidad_llegada"],
    errors="coerce"
)

df_semana["Pendientes"] = pd.to_numeric(
    df_semana["Pendientes"],
    errors="coerce"
)


# =========================
# FILTRO FECHAS
# =========================

rango = st.date_input(
    "📅 Rango Fechas",
    []
)
if len(rango) == 2:

    inicio, fin = rango

    df_filtrado = df[

        (df["Fecha_Llegada"] >= pd.to_datetime(inicio))

        &

        (df["Fecha_Llegada"] <= pd.to_datetime(fin))
    ]

else:

    df_filtrado = df
# =========================
# KPI GENERALES
# =========================
total_pedidos = len(df_filtrado)
kg_solicitados = df_filtrado["Cantidad_Solicitada"].sum()
kg_recibidos = df_filtrado["Cantidad_llegada"].sum()
pendientes = df_semana["Pendientes"].sum()

# =========================
# KPIs
# =========================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.container(border=True)
    st.metric(
    
        "Pedidos%",
        f"{total_pedidos:,.1f}"
    )

with col2:
    st.container(border=True)
    st.metric(
        "Kg Solicitados",
        f"{kg_solicitados:,.1f}"
    )

with col3:
    st.container(border=True)
    st.metric(
        "Kg Recibidos",
        f"{kg_recibidos:,.1f}"
    )

with col4:
    st.container(border=True)
    st.metric(
        "Pendientes",
        f"{pendientes:,.1f}"
    )

# =========================
# ALERTA
# =========================

if pendientes > 10:

    st.warning(
        "⚠️ Alto número de pedidos pendientes"
    )

# =========================
# PEDIDOS POR SEMANA
# =========================

st.subheader(
    "📅 Pedidos por Semana"
)

fig_semana = px.bar(
    df_semana, x="Semana", y=["Llegaron", "Pendientes"],
    barmode="group", title="Pedidos por Semana",
)
fig_semana.update_layout(
    template="plotly_dark", hovermode="x unified",
    xaxis=dict(rangeslider=dict(visible=True)),
)
st.plotly_chart(fig_semana, use_container_width=True)

fig_kg = px.area(
    df_semana, x="Semana", y=["Kg_Solicitados", "Kg_Recibidos"],
    title="Kg Solicitados vs Recibidos",
)
fig_kg.update_layout(
    template="plotly_dark", hovermode="x unified",
    xaxis=dict(rangeslider=dict(visible=True)),
)
st.plotly_chart(fig_kg, use_container_width=True)

# =========================
# PENDIENTES POR ÁREA
# =========================


###GRÁFICO======================
st.subheader(
    "🏭 Pendientes por Área"
)

fig_area = px.treemap(
    df_area, path=["Área"], values="Pendientes",
    color="Pendientes", color_continuous_scale="Reds",
    title="Pendientes por Área",
)
fig_area.update_layout(template="plotly_dark", height=400)
st.plotly_chart(fig_area, use_container_width=True)

fig = px.bar(
    df_filtrado.groupby("Proveedor", as_index=False)["Cantidad_Solicitada"].sum()
              .sort_values("Cantidad_Solicitada", ascending=False),
    x="Proveedor", y="Cantidad_Solicitada",
    color="Cantidad_Solicitada", color_continuous_scale="Viridis",
    text_auto=".2s", title="Cantidad Solicitada por Proveedor",
)
fig.update_layout(template="plotly_dark", hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)
# =========================
# TABLA
# =========================

st.subheader(
    "📋 Detalle por Área"
)

st.dataframe(
    df_area,
    use_container_width=True
)
st.dataframe(
    df_filtrado,
    use_container_width=True
)
# =========================
# EXPORTAR CSV
# =========================

st.download_button(

    "⬇️ Descargar Inventario CSV",

    data=df_area.to_csv(index=False),

    file_name="inventario.csv",

    mime="text/csv"
)
