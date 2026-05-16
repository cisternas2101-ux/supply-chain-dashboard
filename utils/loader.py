import pandas as pd
from utils.connection import get_connection

def load_query(path):

    conn = get_connection()

    with open(path, "r", encoding="latin-1") as file:

        query = file.read()

    df = pd.read_sql(query, conn)

    return df