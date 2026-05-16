	-- Scorecard completo por proveedor
SELECT
    Proveedor,
    COUNT(*) AS Total_OC,
    AVG(DATEDIFF(DAY, Fecha_de_solicitud, Fecha_Llegada))
        AS LeadTime_Prom_Dias,
    ROUND(AVG(CAST(Cantidad_llegada AS FLOAT)
              / Cantidad_Solicitada * 100), 1)
        AS FillRate_Pct,
    ROUND(100.0 * SUM(CASE WHEN Fecha_de_retraso IS NULL
        THEN 1 ELSE 0 END) / COUNT(*), 1)
        AS OnTime_Pct,
    ROUND(100.0 * SUM(CASE WHEN Fecha_de_retraso IS NULL
        AND Cantidad_llegada >= Cantidad_Solicitada
        THEN 1 ELSE 0 END) / COUNT(*), 1)
        AS OTIF_Pct
FROM [dbo].[Programación_Materia_Prima]
GROUP BY Proveedor
ORDER BY OTIF_Pct ASC;
