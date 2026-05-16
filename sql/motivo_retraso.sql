-----Motivo de Retraso----
-- Frecuencia de motivos de retraso
SELECT
    ISNULL(Motivo, 'Sin retraso') AS Motivo,
    COUNT(*) AS Frecuencia,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 1)
        AS Porcentaje
FROM [dbo].[Programación_Materia_Prima]
GROUP BY Motivo
ORDER BY Frecuencia DESC;