import streamlit as st
import pandas as pd

from gurobipy import Model, GRB

from utils.loader import load_query

# =========================
# CONFIG
# =========================

st.set_page_config(
    page_title="Optimización",
    layout="wide"
)

# =========================
# TÍTULO
# =========================

st.title("📈 Optimización de Proveedores") 


st.write(
    "Modelo de optimización usando Gurobi"
)

# =========================
# CARGAR DATOS
# =========================

df_scorecard = load_query(
    "sql/scorecard_proveedores.sql"
)

# =========================
# MOSTRAR DATOS
# =========================

st.subheader("📋 Scorecard")

st.dataframe(
    df_scorecard,
    use_container_width=True
)

# =========================
# BOTÓN OPTIMIZAR
# =========================

if st.button("🚀 Ejecutar Optimización"):

    # =====================
    # PREPARAR DATOS
    # =====================

    df_scorecard["Score"] = (

        df_scorecard["OTIF_Pct"] * 0.4 +

        df_scorecard["FillRate_Pct"] * 0.3 -

        df_scorecard["LeadTime_Prom_Dias"] * 0.3
    )

    # Normalizar score
    scores = (
        df_scorecard
        .set_index("Proveedor")["Score"]
        .to_dict()
    )

    proveedores = list(scores.keys())

    # =====================
    # MODELO
    # =====================

    model = Model("Optimizacion_Proveedor")

    # Variables decisión
    x = model.addVars(

        proveedores,

        lb=0,

        ub=1,

        vtype=GRB.CONTINUOUS,

        name="Asignacion"
    )

    # =====================
    # RESTRICCIÓN
    # =====================

    model.addConstr(

        sum(x[p] for p in proveedores) == 1,

        name="Total_Compra"
    )

    # Máximo 40% proveedor
    for p in proveedores:

        model.addConstr(

            x[p] <= 0.4,

            name=f"Limite_{p}"
        )

    # =====================
    # FUNCIÓN OBJETIVO
    # =====================

    model.setObjective(

        sum(
            scores[p] * x[p]
            for p in proveedores
        ),

        GRB.MAXIMIZE
    )

    # =====================
    # OPTIMIZAR
    # =====================

    model.optimize()

    # =====================
    # RESULTADOS
    # =====================

    resultados = []

    if model.status == GRB.OPTIMAL:

        for p in proveedores:

            resultados.append({

                "Proveedor": p,

                "Asignacion_Optima_%":
                round(x[p].X * 100, 1)
            })

        df_resultado = pd.DataFrame(
            resultados
        )

        # Filtrar solo > 0
        df_resultado = df_resultado[
            df_resultado[
                "Asignacion_Optima_%"
            ] > 0
        ]

        st.success(
            "✅ Optimización completada"
        )

        st.subheader(
            "📊 Resultado Optimización"
        )

        st.dataframe(
            df_resultado,
            use_container_width=True
        )

    else:

        st.error(
            "❌ No se encontró solución óptima"
        )
        
