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
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime
import io


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
# Convertir columnas numéricas
df_scorecard["OTIF_Pct"] = pd.to_numeric(df_scorecard["OTIF_Pct"], errors="coerce")
df_scorecard["FillRate_Pct"] = pd.to_numeric(df_scorecard["FillRate_Pct"], errors="coerce")
df_scorecard["LeadTime_Prom_Dias"] = pd.to_numeric(df_scorecard["LeadTime_Prom_Dias"], errors="coerce")
df_semana["Pendientes"] = pd.to_numeric(df_semana["Pendientes"], errors="coerce")
df_otif["OTIF_Pct"] = pd.to_numeric(df_otif["OTIF_Pct"], errors="coerce")


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

# =========================
# REPORTE PDF
# =========================
 #Reporte========   
st.divider()  # ← agregar
if st.button("📄 Generar Reporte PDF"):

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=inch, leftMargin=inch,
                            topMargin=inch, bottomMargin=inch)
    styles = getSampleStyleSheet()
    story = []

    # Estilos
    titulo = ParagraphStyle("titulo", parent=styles["Heading1"],
                        fontSize=18, textColor=colors.HexColor("#1f3864"))
    seccion = ParagraphStyle("seccion", parent=styles["Heading2"],
                             fontSize=13, textColor=colors.HexColor("#2e75b6"),
                             spaceAfter=6)
    normal = styles["Normal"]

    # Función semáforo
    def semaforo(valor, objetivo=90):
        if valor >= objetivo:
            return " Bueno"
        elif valor >= objetivo * 0.8:
            return " En riesgo"
        else:
            return " Crítico"

    # Función recomendación
    def recomendacion_otif(valor):
        if valor < 80:
            return " OTIF crítico. Se recomienda revisar urgentemente los acuerdos con proveedores y evaluar proveedores alternativos."
        elif valor < 90:
            return " OTIF bajo objetivo. Se recomienda establecer planes de mejora con proveedores críticos y monitorear semanalmente."
        return " OTIF dentro del objetivo. Mantener condiciones actuales y monitorear."

    def recomendacion_lead(valor):
        if valor > 15:
            return " LeadTime elevado. Se recomienda negociar tiempos de entrega y revisar la planificación de compras."
        return " LeadTime dentro del rango aceptable."

    def recomendacion_fill(valor):
        if valor < 90:
            return " Fill Rate bajo. Se recomienda aumentar el stock de seguridad y revisar la disponibilidad de productos."
        return " Fill Rate dentro del objetivo."

    # ── ENCABEZADO ──
    story.append(Paragraph("Reporte de Desempeño de Proveedores", titulo))
    story.append(Paragraph(f"Fecha: {datetime.now().strftime('%d/%m/%Y')}", normal))
    story.append(Spacer(1, 0.3 * inch))

    # ── PREGUNTA 1 ──
    story.append(Paragraph("1. ¿Cómo está el desempeño global de la cadena de suministro?", seccion))
    data_kpi = [
        ["KPI", "Resultado", "Objetivo", "Estado"],
        ["OTIF", f"{otif_global:.1f}%", "90%", semaforo(otif_global)],
        ["Fill Rate", f"{fill_global:.1f}%", "90%", semaforo(fill_global)],
        ["LeadTime Promedio", f"{lead_global:.1f} días", "< 15 días", semaforo(lead_global, 85)],
        ["Órdenes Pendientes", f"{pendientes:,.0f}", "-", "-"],
    ]
    tabla_kpi = Table(data_kpi, colWidths=[2.2*inch, 1.3*inch, 1.2*inch, 1.5*inch])
    tabla_kpi.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f3864")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f2f7ff"), colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
    ]))
    story.append(tabla_kpi)
    story.append(Spacer(1, 0.2 * inch))

    # ── PREGUNTA 2 ──
    story.append(Paragraph("2. ¿Qué proveedores están bajo el objetivo?", seccion))
    criticos = df_scorecard[df_scorecard["OTIF_Pct"] < 90].sort_values("OTIF_Pct")
    if criticos.empty:
        story.append(Paragraph("✅ Todos los proveedores están sobre el objetivo de 90%.", normal))
    else:
        data_crit = [["Proveedor", "OTIF%", "Fill Rate%", "LeadTime (días)"]]
        for _, row in criticos.iterrows():
            data_crit.append([
                str(row["Proveedor"]),
                f"{row['OTIF_Pct']:.1f}%",
                f"{row['FillRate_Pct']:.1f}%" if pd.notna(row['FillRate_Pct']) else "Sin dato",
                f"{row['LeadTime_Prom_Dias']:.1f}"
            ])
        tabla_crit = Table(data_crit, colWidths=[2.5*inch, 1.2*inch, 1.3*inch, 1.2*inch])
        tabla_crit.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#c00000")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#fff0f0"), colors.white]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
        ]))
        story.append(tabla_crit)
    story.append(Spacer(1, 0.2 * inch))

    # ── PREGUNTA 3 ──
    story.append(Paragraph("3. ¿Cuál es el proveedor con mejor desempeño?", seccion))
    top3 = df_scorecard.sort_values("OTIF_Pct", ascending=False).head(3)
    data_top = [["#", "Proveedor", "OTIF%", "Fill Rate%"]]
    for i, (_, row) in enumerate(top3.iterrows(), 1):
        data_top.append([
            f"#{i}",
            str(row["Proveedor"]),
            f"{row['OTIF_Pct']:.1f}%",
            f"{row['FillRate_Pct']:.1f}%"
        ])
    tabla_top = Table(data_top, colWidths=[0.5*inch, 2.5*inch, 1.2*inch, 1.3*inch])
    tabla_top.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e7b34")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f0fff4"), colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
    ]))
    story.append(tabla_top)
    story.append(Spacer(1, 0.2 * inch))

    # ── PREGUNTA 4 ──
    story.append(Paragraph("4. ¿Cuántas órdenes están pendientes?", seccion))
    story.append(Paragraph(f"Total de órdenes pendientes: {pendientes:,.0f}", normal))
    story.append(Spacer(1, 0.2 * inch))

    # ── CARGAR DATOS RETRASOS ──
    df_motivo = load_query("sql/motivo_retraso.sql")
    df_motivo["Frecuencia"] = pd.to_numeric(df_motivo["Frecuencia"], errors="coerce")
    df_motivo["Porcentaje"] = pd.to_numeric(df_motivo["Porcentaje"], errors="coerce")

    # ── PREGUNTA 5: OPTIMIZACIÓN ──
    story.append(Paragraph("5. ¿Cómo distribuir las compras entre proveedores?", seccion))
    story.append(Paragraph(
        "El modelo de optimizacion calcula el porcentaje optimo de compras por proveedor "
        "maximizando OTIF y Fill Rate, minimizando LeadTime, con un maximo de 40% por proveedor.",
        normal
    ))
    top1 = df_scorecard.sort_values("OTIF_Pct", ascending=False).iloc[0]
    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph(
        f"Proveedor recomendado: {top1['Proveedor']} con OTIF de {top1['OTIF_Pct']:.1f}%.",
        normal
    ))
    story.append(Spacer(1, 0.2 * inch))

    # ── PREGUNTA 6: RETRASOS ──
    story.append(Paragraph("6. ¿Cuales son los principales motivos de retraso?", seccion))
    top_motivos = df_motivo.dropna().head(5)
    data_mot = [["Motivo", "Frecuencia", "Porcentaje"]]
    for _, row in top_motivos.iterrows():
        data_mot.append([
            str(row["Motivo"]),
            f"{int(row['Frecuencia'])}",
            f"{row['Porcentaje']:.1f}%"
        ])
    tabla_mot = Table(data_mot, colWidths=[3.5*inch, 1.2*inch, 1.2*inch])
    tabla_mot.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#7b2d00")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#fff5f0"), colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
    ]))
    story.append(tabla_mot)
    story.append(Spacer(1, 0.2 * inch))


    # ── RECOMENDACIONES ──
    story.append(Paragraph("5. Recomendaciones", seccion))
    story.append(Paragraph(recomendacion_otif(otif_global), normal))
    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph(recomendacion_lead(lead_global), normal))
    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph(recomendacion_fill(fill_global), normal))

    # ── GENERAR PDF ──
    doc.build(story)
    buffer.seek(0)

    st.download_button(
        label="⬇️ Descargar Reporte PDF",
        data=buffer,
        file_name=f"reporte_supply_chain_{datetime.now().strftime('%Y%m%d')}.pdf",
        mime="application/pdf"
    )

