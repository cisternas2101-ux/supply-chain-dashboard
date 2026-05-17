import pandas as pd
import os
import streamlit as st
from utils.connection import get_connection

@st.cache_data
def load_query(path):
    
    # Detecta si está en Streamlit Cloud
    en_nube = os.getenv("STREAMLIT_CLOUD") is not None

    if en_nube:
        nombre_archivo = os.path.splitext(os.path.basename(path))[0]
        csv_path = os.path.join("data", f"{nombre_archivo}.csv")
        return pd.read_csv(
        csv_path,
        sep=";",              # ← separador correcto
        encoding="utf-8-sig"  # ← elimina el BOM automáticamente
    )
    
    else:
        # Comportamiento local original, no cambia nada
        conn = get_connection()
        with open(path, "r", encoding="latin-1") as file:
            query = file.read()
        df = pd.read_sql(query, conn)
        return df