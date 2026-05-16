
	-------OTIF--------------
	SELECT 
	Proveedor, 
	COUNT(*) AS Total_Pedidos, 
	SUM(CASE
		WHEN Fecha_de_retraso IS NULL
		AND Cantidad_llegada >= Cantidad_Solicitada
		THEN 1 ELSE 0
		END) AS Pedido_OTIF, 
		ROUND(
		100.0 * SUM(CASE
			WHEN Fecha_de_retraso IS NULL
			AND Cantidad_llegada>= Cantidad_Solicitada
			THEN 1 ELSE 0
			END)/ COUNT(*),2
			)AS OTIF_Pct
	FROM  [dbo].[Programación_Materia_Prima]
	GROUP BY Proveedor
	ORDER BY OTIF_Pct ASC;