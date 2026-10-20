# Resultados reproducibles del handoff mensual

Fuente bruta: 491.506 filas, 10.241 IDs, 21 columnas, enero 1997–marzo 2001, con padding calendario.
Selección propia: 84.251 filas regulares, 8.073 socios, mayo 1997–enero 2001; no reproduce los 7.752 del artículo.
Se registran 397.354 asistencias, media 4,7163/mes elegible, mediana 3; 30,3735 % de meses elegibles con cero.
Comparaciones adyacentes: 73.352; ventanas completas de tres meses: 64.347; de seis: 43.690.
Los conteos son descriptivos de la cohorte, sin intervalo de inferencia ni efecto causal.

Todas las 81.927 claves de Retention v0.5 coinciden en fuente y conteo actual; 2.324 adicionales aquí
corresponden a su exclusión de familias observadas hasta t. Su historial permite algunos meses previos
prorrateados 11/21, mientras aquí solo se usan 1/2. No sustituir estas métricas en su modelo.
No se importaron outcomes, scores ni modelos; no se ajustó otro modelo.

Reproducción: `python scripts/verify_berkeley.py`; `python scripts/build_kaggle.py` crea el notebook portátil.
La ejecución privada real en Kaggle terminó COMPLETE y reprodujo esas cifras. Entorno y evidencia:
[kaggle_validation.json](../reports/berkeley/kaggle_validation.json). El informe local incluye las cinco
figuras de auditoría y [resultados completos](../reports/berkeley/report.md).

Las pruebas temporales incluyen huecos, ventanas incompletas, ceros, recencia desconocida, invariancia
frente a futuro, fronteras overtime y rechazo de claves incompatibles. Fixtures artificiales validan
software; los resultados de Berkeley son evidencia histórica real, no validación operativa actual.
