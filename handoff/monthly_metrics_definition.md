# Definiciones admitidas · Member Behavior mensual

Contrato: [monthly_data_contract.yaml](monthly_data_contract.yaml).
Catálogo completo: [monthly_feature_catalog.csv](monthly_feature_catalog.csv).
Fuente real Berkeley, selección `berkeley_regular_month_v1`; grano socio/mes calendario.
Estos documentos mensuales constituyen el handoff activo de seis piezas. Los archivos sin prefijo
mensual conservan el sandbox sintético y no reemplazan este contrato.

Sea x(t) el conteo registrado en un mes elegible. Solo se publican filas elegibles. Un mes ausente
o excluido rompe la racha. Las ventanas incluyen el mes t; todas las entradas deben estar observadas
en meses consecutivos. El cierre disponible es 00:00 del día siguiente al fin del mes, proxy de
investigación sin reloj de ingesta verificado. Los flags y fronteras se utilizan retrospectivamente
para selección, no como features. No se reconstruye asistencia diaria.

| Métrica | Fórmula/unidad | Nulidad |
| --- | --- | --- |
| recorded_attendance_month | x(t), asistencias registradas | Nunca nula en una fila elegible; cero válido |
| attendance_previous_month | x(t-1), asistencias | Mes anterior no elegible/ausente |
| attendance_change_vs_previous_month | x(t)-x(t-1), diferencia de asistencias | Comparación no disponible |
| attendance_pct_change_vs_previous_month | x(t)/x(t-1)-1, fracción | Anterior ausente o cero |
| attendance_sum_3_calendar_months | Σ x de t-2 a t, asistencias | Menos de 3 meses completos consecutivos |
| attendance_mean_3_calendar_months | Suma anterior / 3, asistencias/mes | Mismo soporte |
| attendance_std_3_calendar_months | √(Σ(x-media)²/3), ddof=0 | Mismo soporte |
| positive_attendance_months_3 | Σ 1[x>0] en 3 meses, meses de 0 a 3 | Mismo soporte |
| attendance_sum_6_calendar_months | Σ x de t-5 a t, asistencias | Menos de 6 meses completos consecutivos |
| attendance_mean_6_calendar_months | Suma anterior / 6, asistencias/mes | Mismo soporte |
| consecutive_eligible_months | Longitud de racha observada hasta t, meses | Siempre ≥1; no es antigüedad contractual |
| months_since_recorded_positive_month | Distancia calendario a último x>0 en la racha, meses | Ningún mes positivo conocido en la racha |

Las medias del reporte agrupan filas socio/mes con métrica no nula. El denominador es ese número de
filas, con personas repetidas; no todos los socios originales ni una muestra igualmente ponderada
por socio. Se informa soporte y número no disponible para cada métrica. Variabilidad cero puede
corresponder a ceros repetidos. Racha y recencia son soporte y proxy mensual, no hábito validado.

Uso admitido: describir volumen, cambios y soporte histórico. No habilita estados, probabilidades,
outreach, visitas diarias ni causalidad. [Metodología detallada](../docs/monthly_methodology.md).
