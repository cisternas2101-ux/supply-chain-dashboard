	-----ON Time-----
	SELECT 
	COUNT(*) AS Total_Pedidos, 
	SUM(CASE WHEN Fecha_de_retraso IS NULL THEN 1 ELSE 0
	END)AS A_Tiempo, 
	SUM(CASE WHEN Fecha_de_retraso IS NOT NULL THEN 1 ELSE 0 END) AS Con_Retraso, 
	ROUND(100.0 * SUM(CASE WHEN Fecha_de_retraso IS NULL THEN 1 ELSE 0 END)
		/ COUNT(*),2)AS Ontime_Pct
	FROM [dbo].[Programación_Materia_Prima];

	SELECT 
	Proveedor, OC, Descripción ,
	Fecha_llegada AS Fecha_Prometida, 
	Fecha_de_retraso AS Fecha_real, 
	DATEDIFF(DAY, Fecha_Llegada, Fecha_de_retraso) AS Dias_Retraso
	FROM [dbo].[Programación_Materia_Prima]
	WHERE Fecha_de_retraso IS NOT NULL
	ORDER BY Dias_Retraso DESC;