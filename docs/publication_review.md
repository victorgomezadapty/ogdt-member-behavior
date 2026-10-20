# Revisión de publicación — 20 de octubre de 2026

Se reconsultó la [página primaria](https://eml.berkeley.edu/~sdellavi/data/gymdata.shtml)
y se leyó `readme.txt` del ZIP exacto fijado por hash. Explican acceso y variables, sin aportar
una licencia explícita de redistribución de la tabla. El copyright de la web no constituye una licencia
abierta de los datos. Resultado: derechos de redistribución **no establecidos**, sin inferir CC0, CC BY o MIT.
No se contactó a los autores ni se publicó un dataset espejo.

El paquete Kaggle incluye nuestro notebook autónomo con atribución, política de selección,
hashes y límites. Descarga desde la URL primaria durante la ejecución o lee un archivo autorizado
por el usuario. El ZIP se almacena temporalmente fuera del directorio de outputs; la tabla y las filas
individuales permanecen en memoria. Solo se guardan JSON y figura agregados. No se adjuntan fuentes,
IDs, derivados por persona, Retention, secretos o rutas de esta máquina.

La licencia MIT del código original OGDT no modifica los derechos de datos, artículo, código del autor
ni Mindweave (CC BY-NC 4.0). Esas fuentes no se incluyen en el paquete de código Berkeley.

La [documentación oficial de metadatos Kaggle](https://github.com/Kaggle/kaggle-cli/blob/main/docs/kernels_metadata.md)
permite ejecutar notebooks privados con Internet. La validación remota se hace en privado. El estado de
ejecución, entorno y resultados se registran en `reports/berkeley/kaggle_validation.json` cuando finaliza.
Una ejecución correcta verifica portabilidad y resultados, no otorga derechos sobre los datos ni
valida estados, predicción o intervención. La publicación pública queda como una acción separada.
