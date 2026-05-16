SELECT
    Proveedor,
    COUNT(*) AS Total_OC,
    AVG(DATEDIFF(DAY, Fecha_de_solicitud, Fecha_Llegada)) AS LeadTime_Promedio,
    MIN(DATEDIFF(DAY, Fecha_de_solicitud, Fecha_Llegada)) AS LeadTime_Minimo,
    MAX(DATEDIFF(DAY, Fecha_de_solicitud, Fecha_Llegada)) AS LeadTime_Maximo
FROM [dbo].[Programación_Materia_Prima]
WHERE Fecha_Llegada IS NOT NULL
GROUP BY Proveedor
ORDER BY LeadTime_Promedio DESC