import pandas as pd
import os
import streamlit as st

from utils.connection import get_connection

# =========================
# LOAD QUERY
# =========================

@st.cache_data
def load_query(path):

    # =====================
    # STREAMLIT CLOUD
    # =====================

    en_nube = (
        "STREAMLIT_CLOUD"
        in os.environ
    )

    # =====================
    # CSV MODE
    # =====================

    if en_nube:

        nombre_archivo = os.path.splitext(
            os.path.basename(path)
        )[0]

        csv_path = os.path.join(
            "data",
            f"{nombre_archivo}.csv"
        )

        return pd.read_csv(
            csv_path,
            sep=";",
            encoding="utf-8-sig"
        )

    # =====================
    # SQL SERVER LOCAL
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