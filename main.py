from utils.loader import load_query

df_otif = load_query("sql/otif.sql")

df_on_time = load_query("sql/on_time.sql")

df_motivo = load_query("sql/motivo_retraso.sql")

df_leadtime = load_query("sql/leadtime.sql")

df_fillrate = load_query("sql/fill_rate.sql")

df_prom_retraso = load_query("sql/prom_retraso.sql")

df_area = load_query("sql/pendiente_por_area.sql")

df_semana = load_query("sql/pendiente_por_semana.sql")

df_scorecard = load_query("sql/scorecard_proveedores.sql")


print(df_otif.head())

print(df_scorecard.head())