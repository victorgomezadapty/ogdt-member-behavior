# Member Behavior mensual · especificación de componente

Propósito: convertir asistencia mensual elegible en 12 métricas descriptivas con soporte y nulidad
explícitos. Entrada: Berkeley exacto, hashes ZIP/tabla y esquema verificados; claves únicas id/time;
selección `berkeley_regular_month_v1`. Salida: una fila por `(dataset_id,member_id,period_end)` elegible,
12 métricas y metadatos definidos en [catálogo](monthly_feature_catalog.csv). No produce outcomes o estados.

Handoff activo: `monthly_data_contract.yaml`, `monthly_feature_catalog.csv`,
`monthly_metrics_definition.md`, `monthly_findings.md`, `monthly_limitations.md` y este documento.
El handoff original de eventos sintéticos queda preservado e independiente.

Implementación del laboratorio: `src/data/berkeley.py`, `src/features/monthly.py`; numpy y pandas.
Verificación: `scripts/verify_berkeley.py`; pruebas en `tests/test_monthly.py`.
Notebook portátil: `publication/kaggle/ogdt_monthly_behavior.ipynb`, construido desde esas mismas funciones
sin imports del repositorio, reports precomputados o Retention; funciona en Kaggle con dependencias incluidas.

Adaptador core: `open-gym-digital-twin/ogdt_core/behavior.py`, biblioteca estándar, sin importar el lab.
Lee export revisado por hash, verifica esquema/identidad/política/cierre/nulidad y recalcula las 12
fórmulas de todas las filas. `MemberMonthBehavior` usa namespace propio de población
`behavior_regular_member_months_v1`. Fuente/version y claves completas preservadas. El puente opcional
a Retention declara explícitamente el mapeo entre esas dos políticas revisadas, coteja todas las claves
y conteos actuales, y devuelve solo evidencia agregada; no mezcla outcomes ni sustituye features.

Fallos: abortar por hash cambiado, duplicado, campo no revisado, fuente/política incompatible, mes no
calendario, valor no finito/no integral actual, reloj incorrecto, fórmula o nulidad discordante. Un cambio
requiere revisión deliberada del manifiesto. Un mes ausente rompe ventanas, no crea una fila cero.
El corte es fecha de cierre disponible proxy ≤ as-of; el core solo expone agregados por métrica/mes.

Alcance aceptable: investigación descriptiva histórica, no operación ni predicción. Métricas candidatas
no son estados de engagement, decisiones o riesgos validados. El pipeline de Retention queda intacto.
