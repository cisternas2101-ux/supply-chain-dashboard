import pandas as pd
import streamlit as st

from utils.connection import get_connection

# =========================
# MODO
# =========================

USE_CSV = True

# =========================
# LOAD QUERY
# =========================

@st.cache_data

def load_query(path):

    # ---------------------
    # CSV MODE
    # ---------------------

    if USE_CSV:

        csv_path = (

            path

            .replace("sql/", "data/")

            .replace(".sql", ".csv")
        )

        return pd.read_csv(csv_path)

    # ---------------------
    # SQL MODE
    # ---------------------

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