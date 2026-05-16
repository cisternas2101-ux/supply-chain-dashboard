
--------Fill  rate-------
SELECT
Proveedor, 
Descripción, 
Cantidad_Solicitada, 
Cantidad_Llegada, 
ROUND(
	CAST(Cantidad_llegada AS FLOAT)/ Cantidad_Solicitada * 100,2) 
	AS Fill_Rate_Pct, 
	CASE
	WHEN Cantidad_llegada >= Cantidad_Solicitada THEN 'Completo'
	WHEN Cantidad_Llegada >0 THEN 'Parcial'
	ELSE 'Sin entrega'
  END AS Estado_Entrega
FROM [dbo].[Programación_Materia_Prima]
ORDER BY Fill_Rate_Pct ASC

SELECT 
	ROUND(AVG(CAST(Cantidad_llegada AS FLOAT)/ Cantidad_Solicitada * 100),2)
	AS Fill_Rate_Global
	FROM [dbo].[Programación_Materia_Prima]