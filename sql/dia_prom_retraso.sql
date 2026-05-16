-- Días promedio de retraso por motivo
SELECT
    Motivo,
    COUNT(*) AS Casos,
    AVG(DATEDIFF(DAY, Fecha_Llegada, Fecha_de_retraso))
        AS Dias_Retraso_Prom
FROM [dbo].[Programación_Materia_Prima]
WHERE Motivo IS NOT NULL
GROUP BY Motivo
ORDER BY Dias_Retraso_Prom DESC;
