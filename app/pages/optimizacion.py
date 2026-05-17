import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import streamlit as st
import pandas as pd
from utils.loader import load_query

# =========================
# DETECTAR SOLVER
# =========================
_SOLVER = None

try:
    from gurobipy import Model, GRB
    _SOLVER = "gurobi"
except ImportError:
    pass

if _SOLVER is None:
    try:
        from pulp import LpMaximize, LpProblem, LpVariable, lpSum, value, LpStatus
        _SOLVER = "pulp"
    except ImportError:
        pass

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Optimización", layout="wide")
st.title("📈 Optimización de Proveedores")
st.write("Modelo de optimización de asignación a proveedores")

# =========================
# CARGAR DATOS
# =========================

df_scorecard = load_query("sql/scorecard_proveedores.sql")

# Convertir columnas numéricas
def convertir_numericos(df):
    for col in df.select_dtypes(exclude="number").columns:
        converted = pd.to_numeric(df[col], errors="coerce")
        if converted.notna().sum() / len(df) > 0.5:
            df[col] = converted
    return df

df_scorecard = convertir_numericos(df_scorecard)



# =========================
# MOSTRAR DATOS
# =========================
st.subheader("📋 Scorecard")
st.dataframe(df_scorecard, use_container_width=True)

# =========================
# BOTÓN OPTIMIZAR
# =========================
if _SOLVER is None:
    st.error("❌ No hay solver disponible")

elif st.button("🚀 Ejecutar Optimización"):

    # Eliminar filas con NaN en columnas clave
    df_opt = df_scorecard.dropna(
        subset=["OTIF_Pct", "FillRate_Pct", "LeadTime_Prom_Dias", "Proveedor"]
    )

    df_opt["Score"] = (
        df_opt["OTIF_Pct"] * 0.4 +
        df_opt["FillRate_Pct"] * 0.3 -
        df_opt["LeadTime_Prom_Dias"] * 0.3
    )

    scores = df_opt.set_index("Proveedor")["Score"].to_dict()
    proveedores = list(scores.keys())

    if _SOLVER == "gurobi":
        model = Model("Optimizacion_Proveedor")
        x = model.addVars(proveedores, lb=0, ub=0.4, vtype=GRB.CONTINUOUS, name="Asignacion")
        model.addConstr(sum(x[p] for p in proveedores) == 1, name="Total_Compra")
        model.setObjective(sum(scores[p] * x[p] for p in proveedores), GRB.MAXIMIZE)
        model.optimize()
        optimo = model.status == GRB.OPTIMAL
        resultado_fn = lambda p: x[p].X

    elif _SOLVER == "pulp":
        model = LpProblem("Optimizacion_Proveedor", LpMaximize)
        x = {p: LpVariable(f"x_{p}", lowBound=0, upBound=0.4) for p in proveedores}
        model += lpSum(scores[p] * x[p] for p in proveedores)
        model += lpSum(x[p] for p in proveedores) == 1
        model.solve()
        optimo = LpStatus[model.status] == "Optimal"
        resultado_fn = lambda p: value(x[p])

    if optimo:
        resultados = [
            {"Proveedor": p, "Asignacion_Optima_%": round(resultado_fn(p) * 100, 1)}
            for p in proveedores
        ]
        df_resultado = pd.DataFrame(resultados)
        df_resultado = df_resultado[df_resultado["Asignacion_Optima_%"] > 0]
        st.success("✅ Optimización completada")
        st.subheader("📊 Resultado Optimización")
        st.dataframe(df_resultado, use_container_width=True)
    else:
        st.error("❌ No se encontró solución óptima")