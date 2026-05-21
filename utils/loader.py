import pandas as pd
import os
import io
import streamlit as st

from utils.connection import get_connection


@st.cache_data
def load_query(path):

    # =====================
    # DETECTAR STREAMLIT CLOUD
    # =====================

    en_nube = os.path.exists("/mount/src")

    # =====================
    # CSV CLOUD
    # =====================

    if en_nube:

        nombre_archivo = os.path.splitext(
            os.path.basename(path)
        )[0]

        csv_path = os.path.join(
            "data",
            f"{nombre_archivo}.csv"
        )

        with open(csv_path, "r", encoding="utf-8-sig", errors="replace") as f:
            contenido = f.read()

        df = pd.read_csv(
            io.StringIO(contenido),
            sep=";",
            quoting=3,
            escapechar="\\",
            na_values=["NULL", "null", ""],
            keep_default_na=True,
            on_bad_lines="skip",
        )

        # Limpiar espacios en nombres de columnas
        df.columns = df.columns.str.strip()

        return df

    # =====================
    # SQL LOCAL
    # =====================

    conn = get_connection()

    with open(
        path,
        "r",
        encoding="latin-1"
    ) as file:

        query = file.read()

    df = pd.read_sql(
        query,
        conn
    )

    conn.close()

    return df