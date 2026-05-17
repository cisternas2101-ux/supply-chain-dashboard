import pyodbc

def get_connection():

    conn = pyodbc.connect(

        "DRIVER={SQL Server};"
        "SERVER=LAPTOP-DR8C1BKS\\MSSQLSERVER01;"
        "DATABASE=Compras-2026;"
        "Trusted_Connection=yes;"
    )

    return conn
