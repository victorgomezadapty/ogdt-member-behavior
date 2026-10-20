# Adaptador mensual Berkeley — definiciones y límites

La decisión de fuente precede al pipeline y consta en [plan](project_plan.md) y [adecuación](data_readiness.md). Esta investigación usa registros históricos reales de gimnasio, separados del sandbox sintético. No se entrenan modelos ni se adjudican resultados contractuales.

## Grano, clave e identidad

Una fila de origen corresponde a un ID y mes. La clave canónica es `(dataset_id, member_id, period_end)`, con `dataset_id=berkeley_gym_aer_2006`, `member_id=str(int(id))` y `period_end` como último día calendario del mes MATLAB `time`. `as_of_exclusive` es el día siguiente a `period_end` a medianoche; no es el timestamp de una visita ni una ingesta verificada.

La fuente tiene 491.506 filas de calendario y 10.241 IDs; muchos meses son relleno sin contrato. Se preserva una tabla de elegibilidad con todas las claves; la tabla de métricas contiene solo meses elegibles. Una ausencia tras un left join con Retention significa **métrica mensual no disponible bajo esta política**, nunca asistencia cero. Las claves y hashes permiten comprobar identidad de la población, pero no hacen equivalentes dos políticas de selección.

## Política conservadora de meses regulares

Exigir simultáneamente `contract in {1,2}`, `duplicate=0`, `problem=0`, `overtime=0`, `time >= begatt`, `time <= endatt`, y mes dentro de abril de 1997–julio de 2000 para club 11 o abril de 1997–febrero de 2001 para clubes 13/16. Los flags son del autor; un flag duplicate no equivale a duplicar `(id,time)`. No se descartan silenciosamente sus filas originales: quedan auditadas, con asistencia analítica nula.

Los códigos prorrateados, promociones, transiciones, congelaciones, impagos y meses sin contrato quedan fuera del análisis principal. No se reconstruyen todos los spells ni exclusiones por familia; esto no reproduce la muestra del artículo. La selección favorece meses regulares y modifica la composición/seguimiento de la muestra. La comparación por tipo contractual es descriptiva y no identifica efectos causales.

El archivo contiene asistencias del club 11 en agosto de 2000 aunque `overtime=1`. Prevalece su exclusión explícita y el periodo publicado; una asistencia positiva no acredita elegibilidad. Un cero de un mes elegible se conserva como conteo registrado; no prueba ausencia absoluta o un estado Dormant.

## Métricas y ventanas

El catálogo [monthly_feature_catalog.csv](../handoff/monthly_feature_catalog.csv) define cada campo con significado, requisitos, ventana y limitaciones. Todas las ventanas contienen el mes actual y los anteriores; no usan futuros meses. Requieren consecutividad calendario y elegibilidad en todos los meses necesarios. Un hueco, flag excluyente o mes no regular interrumpe el historial. No se extienden ventanas sobre el siguiente mes válido.

- `recorded_attendance_month`: `attend` del mes elegible, en asistencias registradas.
- `attendance_previous_month`: conteo del mes calendario inmediatamente anterior, solo si ambos meses son elegibles y consecutivos.
- `attendance_change_vs_previous_month`: actual − anterior. Un signo negativo no es un estado validado de disengagement.
- `attendance_pct_change_vs_previous_month`: actual/anterior − 1; nulo si falta el mes previo o si su conteo es 0.
- `attendance_sum_3_calendar_months` / `attendance_mean_3_calendar_months`: suma de tres meses consecutivos elegibles y esa suma/3. No es `visits_90d`.
- `attendance_std_3_calendar_months`: desviación estándar poblacional (`ddof=0`) de esos tres conteos; 0 en tres ceros no significa hábito estable.
- `positive_attendance_months_3`: número de meses con conteo >0 dentro de la misma ventana completa de tres; rango 0–3. No es frecuencia semanal ni semanas activas.
- `attendance_sum_6_calendar_months` / `attendance_mean_6_calendar_months`: suma y media de seis meses consecutivos elegibles. Si falta uno, nulo.
- `consecutive_eligible_months`: longitud de la racha observada y elegible que acaba en el mes actual. No es antigüedad contractual ni fecha de alta.
- `months_since_recorded_positive_month`: distancia en meses calendario al último mes con conteo >0 dentro de la racha elegible actual. El mes positivo actual vale 0. Si la racha solo contiene ceros, nulo: se desconoce el último mes positivo antes del borde o hueco. No es recencia de visita en días.

No se calculan métricas diarias de 7/30/90 días, preferencias por día/hora, visitas entre sedes o cancelaciones individuales desde este agregado mensual. No se inventa el detalle que falta.

## Auditoría de elegibilidad

`member_month_eligibility.csv` mantiene las tres claves, club y `source_contract_code` como contexto. `excluded_outside_documented_span`, `excluded_author_duplicate`, `excluded_author_problem`, `excluded_overtime` y `excluded_nonregular_contract` son flags que pueden solaparse. `attendance_eligible` es la conjunción de sus negaciones. `eligibility_status` describe esa decisión; `recorded_attendance_month` es nulo en cualquier fila excluida. Estos campos de revisión no son predictores ni labels conductuales.

Los conteos de exclusión secuencial muestran una cascada y no deben sumarse con los flags solapados. Los resúmenes por mes/club incluyen número de filas elegibles, miembros, suma/media/mediana y fracción de ceros registrados. El histograma y la media global ponderan meses-persona; no son promedios con igual peso por socio. La gráfica temporal refleja una composición variable de meses regulares, no la asistencia completa del gimnasio ni una estacionalidad validada.

Las seis trayectorias ilustrativas se eligen determinísticamente por rangos de volumen total entre quienes tienen al menos seis meses elegibles. Se etiquetan A–F en el gráfico; los meses no elegibles o no disponibles quedan como cortes/nulos, no ceros. No son una muestra representativa ni estados de engagement.

## Tiempo, integración y disponibilidad

La hipótesis de investigación es disponer de la asistencia agregada al cierre mensual. No hay reloj de ingesta, histórico de revisiones ni validación de disponibilidad en producción. Los límites del extracto y flags retrospectivos solo seleccionan/auditan; se excluyen de la tabla de features, junto a fechas finales contractuales, demografía y precios. La corrección temporal de ventanas no elimina el sesgo de selección retrospectivo.

La comprobación con Retention usa hashes de origen y las tres claves completas. En la revisión final del 20 de octubre se leyó su contrato v0.5 y su export real de features: 81.927 claves compartidas y conteos actuales idénticos; las 2.324 filas que solo están aquí cumplen su exclusión acumulada de familia observada hasta t. No se unen personas de Mindweave o Lisboa.

Retention representa el cierre como último nanosegundo del mes; aquí se usa la frontera exclusiva al inicio del día siguiente. Se verifica `as_of_exclusive = prediction_date + 1 ns`; el join se hace por `period_end`, no por esos timestamps distintos. Retention admite historia prorrateada 11/21 dentro de episodios; nuestro historial exige meses regulares. En 6.964 claves su mes previo está disponible y el nuestro no; en 6.712 ocurre para su ventana de tres meses. Cuando ambas ventanas están disponibles, se comprueba acuerdo tras invertir su log1p. Esto no permite reemplazar sus features/modelo con las nuestras.

Su target `berkeley_clear_transition_v1` y benchmark histórico ya existen, con alcance de estados claros y disponibilidad proxy. No se importaron outcomes, scores ni modelos en Member Behavior. Se cotejaron únicamente claves, conteos, cobertura de features y fronteras; este puente no valida resultados operativos, intervenciones o estados de engagement. El JSON de integración fija también hashes del export y contrato leídos.

## Alcance de la evidencia

Son datos reales históricos de tres clubes, con una política propia de meses regulares. No validan comportamiento de gimnasios actuales, predicción, engagement latente ni beneficio causal de contactar a un socio. Revisar términos de publicación antes de redistribuir filas del original o derivados identificables. Los archivos por persona se generan solo localmente y quedan ignorados por Git.
