import pandas as pd
import os
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

        return pd.read_csv(
            csv_path,
            sep=None,
            engine="python",
            encoding="utf-8-sig"
        )

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
