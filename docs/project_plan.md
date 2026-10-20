# Plan vigente — comportamiento mensual con una fuente fitness real

Decisión registrada el **19 de octubre de 2026**, antes de construir el adaptador mensual. Se revisaron la memoria del workspace, el plan y la evaluación de Retention, documentación primaria y el archivo original. El laboratorio conserva su pregunta: comprender trayectorias de asistencia sin equiparar comportamiento, engagement y baja contractual.

## Actualización de cierre — 20 de octubre de 2026

Retention avanzó durante la ejecución. Su contrato v0.5 y su definición `berkeley_clear_transition_v1` ya adjudican un target histórico acotado; existe un benchmark propio y export canónico. Se releyeron esos documentos y se cotejó el export efectivo: **81.927 claves compartidas**, conteos actuales iguales y fronteras mensuales equivalentes; **2.324 filas adicionales de Member Behavior** se explican por la exclusión de familias observadas hasta t en Retention. Además, sus ventanas admiten meses previos prorrateados 11/21, mientras aquí se requieren regulares 1/2. Estas features no se sustituyen automáticamente en su modelo. Se conserva la separación de outcomes/scores y no se modifica Retention. Ver `reports/berkeley/integration_readiness.json`.

Las referencias a target o adquisición pendientes en las secciones siguientes documentan la evaluación inicial del 19 de octubre; esta actualización prevalece para el estado actual. Retention también declara verificada la equivalencia primaria del CSV de Lisboa; Member Behavior no lo procesa ni vuelve a validar esa equivalencia. Continúan fuera de validación el uso operativo, la ingesta real, los estados ambiguos y la generalización a gimnasios actuales.

## Evaluación durante el plan

**Berkeley, Paying Not to Go to the Gym**, procede de gimnasios reales. Se inspeccionó `GymAERSourceData.dta` dentro del ZIP del autor: 491.506 filas, 10.241 identificadores, 21 columnas y clave `(id,time)` única. El archivo público es socio/mes; `time` marca el inicio del mes en fecha MATLAB y `attend` es el conteo mensual. Su calendario bruto abarca enero de 1997–marzo de 2001 e incluye meses fuera de seguimiento y sin contrato. Tener una fila no equivale a tener exposición de asistencia. El artículo y el código del autor complementan las etiquetas del archivo.

**Mindweave** sigue siendo útil para comprobar software con eventos sintéticos. Sus 2.000 check-ins cubren solo 32 de 300 miembros; esa muestra no valida comportamientos reales ni debe ampliarse para aparentar evidencia fitness. Se conservan sus notebooks, métricas y reportes como referencia metodológica, separados de Berkeley.

**Lisboa** corresponde a otra población. La documentación primaria describe datos reales de una instalación deportiva. En Retention ya existe un CSV adquirido de un espejo con procedencia registrada; la equivalencia byte a byte con el archivo primario no está confirmada. Sus campos agregados de fin de relación no sirven para crear una secuencia mensual histórica. Este hito no lo procesa ni lo une con Berkeley.

## Alcance que sí permiten los datos

1. Congelar localmente el ZIP ya adquirido por Retention, comprobar hashes y preservar nombres/etiquetas originales. No modificar Retention ni publicar los datos originales.
2. Auditar meses, flags, códigos y fronteras por club. Separar cobertura de filas calendario y de elegibilidad contractual.
3. Construir un adaptador descriptivo mensual con clave `(dataset_id, member_id, period_end)` y métricas de ventanas de meses calendario. No convertirlas en visitas diarias o ventanas exactas de 30/90 días.
4. Usar como análisis principal un subconjunto explícito de meses regulares: `contract in {1,2}`, `duplicate=0`, `problem=0`, `overtime=0` y fechas dentro de límites de asistencia y del periodo publicado por centro. Los meses excluidos permanecen auditados; su asistencia analítica es desconocida/no aplicable, nunca un cero imputado.
5. Comparar meses adyacentes y calcular ventanas de tres/seis meses solo cuando todos los meses consecutivos tienen asistencia elegible. No atravesar huecos, meses congelados, prorrateados o fuera de captura. Mantener los ceros que sí están registrados en meses elegibles.
6. Describir distribuciones, trayectoria temporal y variación individual con denominadores explícitos. Entregar diccionario mensual, reporte, notebook y contrato de integración.

## Fronteras y decisiones comprobadas

El club 1 tiene filas de agosto de 2000 con asistencia positiva, pero `overtime=1`; se excluyen. El periodo publicado termina en julio de 2000 para ese club. Para los clubes 2 y 3 termina en febrero de 2001. Estos límites se combinan con los metadatos de fuente; no basta con `time <= endatt`.

Las 491.506 filas contienen 374.853 códigos contractuales 0. No son 374.853 casos de disengagement. El código 7 mezcla congelación/cancelación dentro del mes; 70 identifica impago en la documentación; ninguno se transforma en un target de churn en este laboratorio. La selección principal deliberadamente excluye esos meses.

No se reproduce la muestra publicada de 7.752 socios: faltan las exclusiones completas por spell/familia/promociones. Se etiquetará el subconjunto como **meses de contrato regular de la fuente bruta**, con sus propias cifras y límites. No se reconstruye antigüedad desde el primer mes visible como si fuera la fecha real de alta.

## Enlace y temporalidad

El ZIP inspeccionado tiene SHA-256 `f2abbaa0312b697c56892621782073a8dd4b0fbf7cdbb8b9746a28c6398772f9`, coincidente con la fuente de Retention; su tabla tiene SHA-256 `e56ffe6177eb5e1508555d07a756a58f9e74d051eed12601ab5a34919949289c`. Se utilizará `dataset_id=berkeley_gym_aer_2006`, `member_id=str(int(id))` y `period_end` como último día calendario. Es una compatibilidad comprobada de población/origen, no una autorización para usar labels todavía no adjudicados.

Las métricas en el cierre de mes usan exclusivamente el mes actual y pasados. Disponibilidad en ese cierre es una hipótesis de investigación; no existe reloj de ingesta. Las fechas finales del extracto, flags y correcciones retrospectivas condicionan selección/auditoría, pero no son predictores. El target y seguimiento contractual permanecen en Retention, aún pendientes de adjudicación. No se entrenan modelos ni se asignan estados finales en esta continuación.

## Pendiente y criterio de aceptación

Verificar conservación de claves, nulidad ante huecos, ventanas sin información futura y compatibilidad exacta con el archivo compartido; guardar evidencia ejecutable. Documentar permisos de redistribución antes de publicar filas originales o derivados identificables. No extrapolar este estudio histórico a gimnasios actuales, Optimo o decisiones de intervención. Estados/segmentos/riesgo requieren una fase posterior con semántica, objetivo y validación explícitos.

Fuentes primarias: [página de datos del autor](https://eml.berkeley.edu/~sdellavi/data/gymdata.shtml), [artículo](https://eml.berkeley.edu/~sdellavi/wp/gymemp06-03-19.pdf), README y `DataGymAERMar06.do` dentro del archivo inspeccionado. [Lisboa: ficha primaria](https://data.mendeley.com/datasets/yprk4jdgnv/1). La procedencia y decisiones adicionales quedan en `docs/data_readiness.md`.
