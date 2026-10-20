# Diccionario de origen mensual — Berkeley

Datos históricos reales de gimnasio. El archivo de origen contiene 491.506 filas y 21 variables; las etiquetas siguientes se extraen del Stata inspeccionado. No se publican valores demográficos ni IDs en este documento. Ver [adecuación](data_readiness.md) y [metodología](monthly_methodology.md) antes de interpretar columnas.

| Field | Stata label | Parsed type | Nulls |
| --- | --- | --- | --- |
| id | Individual identifier | int32 | 0 |
| time | First day of the month, MATLAB code | float32 | 0 |
| attend | Number of monthly attendances | int8 | 0 |
| contract | Detailed contract type | int16 | 0 |
| imprice | Imputed price by contract type | int8 | 0 |
| trprice | Price recorded in billing system | int8 | 0 |
| code | Code for the transaction | int16 | 0 |
| init | Initiation fee paid | int16 | 0 |
| problem | Problem with observation | int16 | 0 |
| club | 11 is Club 1, 13 is Club 2, 16 is Club 3 | int8 | 0 |
| birthday | Birthday of member | float64 | 27296 |
| female | Member is female | float64 | 511 |
| age | Age of member | float64 | 27296 |
| month | Month and year of observation | int8 | 0 |
| begatt | MATLAB code for April 1 1997 -- Date Data starts | float32 | 0 |
| endatt | Last month in which attendance data available | float32 | 0 |
| endcont | Last month in which contract data is available | float32 | 0 |
| endcontp | Last effective month | float32 | 0 |
| overtime | Indicator for observations beyond end of attendance data | int8 | 0 |
| dlocker | Member rents a locker in that month | int8 | 0 |
| duplicate | Indicator for duplicate observation, needs to be dropped | int8 | 0 |

Los límites y flags se usan para revisión, no como predictores. `contract` pertenece al contexto de selección y al trabajo de Retention; no es un target de churn automático. `time` representa un mes, no una visita. `birthday`, demografía y precios no se utilizan en el adaptador. Las definiciones de los campos derivados están en el [catálogo mensual](../handoff/monthly_feature_catalog.csv).
