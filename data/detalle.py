df = load_query("sql/detalle.sql")

df.to_csv(
    "data/detalle.csv",
    index=False
)