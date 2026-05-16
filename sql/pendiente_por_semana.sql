-- Pendientes por semana
SELECT
    Semana,
    COUNT(*) AS Total_Pedidos,
    SUM(CASE WHEN Estado = 'LLEGÓ'    THEN 1 ELSE 0 END) AS Llegaron,
    SUM(CASE WHEN Estado = 'EN ESPERA' THEN 1 ELSE 0 END) AS Pendientes,
    SUM(Cantidad_Solicitada)  AS Kg_Solicitados,
    SUM(Cantidad_llegada)     AS Kg_Recibidos
FROM [dbo].[Programación_Materia_Prima]
GROUP BY Semana
ORDER BY Semana;
