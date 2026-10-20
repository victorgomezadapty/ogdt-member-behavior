# Adecuación y decisión de fuente — 19 de octubre de 2026

Esta evaluación precede a la implementación del adaptador mensual. Se basa en documentación primaria y en la inspección efectiva del archivo local; no en el nombre comercial de un dataset.

**Actualización final del 20 de octubre:** el estado inicial se conserva abajo como historial de evaluación. Retention v0.5 ya dispone de un target mensual propio y benchmark histórico; su export real de 81.927 features mensuales se cotejó con Member Behavior. Todas sus claves encuentran correspondencia y las 2.324 filas adicionales de nuestro subconjunto se explican por familia observada hasta t. Conteos actuales y fronteras temporales concuerdan. Las ventanas históricas tienen políticas diferentes, por lo que las features no son sustitutos directos del modelo de Retention. No se cargaron outcomes ni scores. La evidencia exacta y los hashes del export/contrato están en [integración](../reports/berkeley/integration_readiness.json).

El informe actual de Retention declara equivalencia primaria del CSV de Lisboa y target adjudicado; las menciones de esos pendientes en la evaluación inicial ya no describen su estado actual. Este laboratorio mantiene Lisboa fuera del pipeline y no afirma una verificación primaria independiente de ese archivo.

| Criterio | Berkeley | Mindweave | Lisboa |
| --- | --- | --- | --- |
| Dominio y origen | Gimnasios reales; fuente pública de replicación del autor | Cadena de gimnasio simulada; muestra pública sintética | Instalación deportiva real según ficha primaria; CSV local en Retention obtenido de espejo |
| Unidad | Persona/mes; 21 columnas | Miembro, check-in sintético, plan, sede | Persona agregada; no panel mensual libre |
| Identidad y enlace | `(id,time)` única; misma fuente/hash que Retention | IDs de otra población, sin enlace con Berkeley | Otra población; prohibido unir personas con las otras fuentes |
| Conducta | `attend`, conteo mensual | Eventos con reloj, captura incompleta | Agregados de uso y de fin de relación; no reconstruir snapshots |
| Tiempo y cobertura | Calendario bruto 1997-01 a 2001-03; límites y overtime por centro | Fechas 2023–2024; solo 32 miembros con visitas | Las columnas del CSV adquirido incluyen fechas y resúmenes de final de relación; inspección semántica corresponde a Retention |
| Resultados contractuales | `contract` detallado; target/censura pendientes | cancel_date/is_active sintéticos | Dropout de la propia fuente, no equivalente automáticamente |
| Alcance aceptado aquí | Investigación descriptiva de asistencia mensual de contratos regulares; interfaz compartida | Sandbox preservado, no evidencia real | Fuera del nuevo pipeline; comparación independiente posterior |

## Comprobado directamente

- Hash ZIP y hash Stata coinciden con el origen auditado en Retention. No se reutilizan IDs parecidos de poblaciones distintas.
- 491.506 filas, 10.241 IDs, 51 meses calendario, claves únicas y sin huecos en la malla bruta por ID. La malla incluye meses sin contrato; no acredita seguimiento continuo.
- `attend` es entero no negativo (0–42). Flags y límites de seguimiento existen; las ausencias demográficas no se imputan porque no se usan.
- `duplicate` marca 1.234 filas aunque `(id,time)` sea única: significa un problema de registro de persona del autor, no una clave duplicada ordinaria.
- Hay 16.532 filas con `overtime=1` y 76.909 con `problem != 0`. Se auditan y se excluyen del subconjunto principal.
- El club 1 tiene 5.181 asistencias registradas en agosto de 2000, mes marcado overtime para sus 4.468 filas. Se excluye en lugar de presentar ese mes como captura regular.
- Meses principales antes de agregar métricas: 84.251 filas regulares correspondientes a 8.073 miembros, tras filtros explícitos. Este conteo no reproduce la muestra del artículo.

## Hipótesis y pendientes

- Se asume disponibilidad al cierre mensual para estudiar features retrospectivos; el archivo no conserva ingesta ni revisiones históricas. No es una evaluación point-in-time de producción.
- Los meses regulares se seleccionan conservadoramente, no como prueba de seguimiento perfecto. El artículo discute posibles errores de registro; un cero elegible es un cero mensual registrado, no ausencia absoluta probada.
- Las exclusiones completas del artículo, contratos/prorrateos y spells siguen sin reproducirse. No llamar a esta muestra la de 7.752 personas ni asignar una fecha de alta desde el borde izquierdo.
- Fin de contrato, baja voluntaria, congelación e impago requieren definición y censura en Retention. No se asignan labels ni se mezclan sus variables de fin de seguimiento con los predictores de conducta.
- Los términos de redistribución del archivo de Berkeley no están resueltos. Trabajo local de investigación; raw y derivados por persona quedan fuera de Git y de publicación.
- La equivalencia del CSV de Lisboa con los bytes de la fuente primaria está pendiente; el manifiesto de Retention indica espejo atribuido. Esta continuación no lo procesa ni modifica sus archivos.

## Decisión

**Apto para EDA de conducta mensual, con selección y cobertura auditadas. No apto todavía para estados validados, churn prediction o intervención operacional.** Adoptar Berkeley como investigación activa de Member Behavior permite compartir identidad real con Retention; conservar Mindweave como evidencia de software y metodología exclusivamente sintética.

Referencias: [Berkeley](https://eml.berkeley.edu/~sdellavi/data/gymdata.shtml), [artículo y apéndice de datos](https://eml.berkeley.edu/~sdellavi/wp/gymemp06-03-19.pdf), README y código original dentro del ZIP. Evaluación de Retention consultada en `../ogdt-retention/docs/project_plan.md` y `../ogdt-retention/docs/data_readiness.md`; se dejan intactas.
