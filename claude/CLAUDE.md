# Supply Chain Analytics App

## Goal
Professional logistics/supply-chain analytics portfolio project (Power BI/Tableau style) with Gurobi optimization.

---

## Stack
- **Frontend:** Streamlit (multipage), Plotly Express
- **Backend:** Python, Pandas, PyODBC
- **Optimization:** Gurobi
- **Database:** SQL Server

---

## DB Connection
```python
pyodbc.connect(
    "DRIVER={SQL Server};"
    "SERVER=LAPTOP-DR8C1BKS\\MSSQLSERVER01;"
    "DATABASE=Compras-2026;"
    "Trusted_Connection=yes;"
)
```
- Connection managed in: `utils/connection.py`
- All queries loaded via: `utils/loader.py` → `load_query(sql_file)`
- Main table: `[dbo].[Programación_Materia_Prima]`

---

## Project Structure
```
app/
  dashboard.py              # Main entry point
  pages/
    proveedores.py          # Supplier scorecard & KPIs
    retrasos.py             # Delay analysis
    inventario.py           # Inventory & replenishment tracking
    optimizacion.py         # Gurobi supplier optimization
    resumen_ejecutivo.py    # Executive summary

sql/
  otif.sql
  fill_rate.sql
  leadtime.sql
  scorecard_proveedores.sql
  motivo_retraso.sql
  prom_retraso.sql
  pendiente_por_area.sql
  pendiente_por_semana.sql
  detalle.sql

utils/
  connection.py             # DB connection (do not modify credentials)
  loader.py                 # load_query() function
```

---

## KPIs
- **OTIF** – On Time In Full
- **Fill Rate** – % of orders fulfilled
- **Lead Time** – Average delivery time
- **OnTime** – % delivered on time
- **Pending Orders** – Open/pending purchase orders

---

## Gurobi Optimization
**Objective (maximize):**
```
0.4 * OTIF + 0.3 * FillRate - 0.3 * LeadTime
```
**Constraints:**
```
sum(x) = 1      # weights must sum to 1
x <= 0.4        # no single supplier > 40%
```
- Located in: `pages/optimizacion.py`

---

## Features
- Multipage Streamlit app
- Supplier filter (sidebar)
- Date range calendar filter (sidebar)
- KPI metrics cards
- Plotly charts (dark theme)
- CSV export buttons
- Supplier scorecards
- Inventory / replenishment tracking
- Delay analysis (by reason, by area, by week)
- Gurobi supplier optimization

---

## UI Conventions
- Dark theme throughout (`plotly` layout template: `plotly_dark`)
- Sidebar for all filters
- `st.metric()` for KPI cards
- `st.tabs()` for section separation
- Responsive charts via `use_container_width=True`

---

## Code Conventions
- Each page is self-contained in `pages/`
- Filters (supplier, date range) passed as parameters to SQL queries
- Charts always use `px` (plotly.express)
- DataFrames loaded via `load_query(sql_file, params)`

---

## Do NOT Modify
- `utils/connection.py` – DB credentials
- `sql/` files – unless explicitly asked
- Gurobi model constraints – unless explicitly asked
