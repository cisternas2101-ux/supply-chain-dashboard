-- Por área
SELECT
    Área,
    COUNT(*) AS Total,
    SUM(CASE WHEN Estado = 'EN ESPERA' THEN 1 ELSE 0 END) AS Pendientes,
    SUM(Cantidad_Solicitada) AS Total_Kg
FROM [dbo].[Programación_Materia_Prima]
GROUP BY Área
ORDER BY Pendientes DESC;