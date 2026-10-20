# Member Behavior — decisión de fuente vigente

Leer `../PROJECT_MEMORY.md`, `docs/project_plan.md` y `docs/data_readiness.md` antes de ampliar datos, pipelines, estados o modelos. Rigen las instrucciones de `../AGENTS.md`.

La investigación activa usa Berkeley mensual, de dominio fitness real, bajo el mismo `dataset_id` y bytes de origen que Retention. Mindweave se conserva como sandbox sintético separado. No borrar ni confundir sus resultados. No fabricar eventos diarios, recencia en días, horarios o estados validados a partir de conteos mensuales. No unir personas entre Berkeley, Lisboa y Mindweave. Un join con Retention debe verificar fuente/hash y la clave completa `(dataset_id, member_id, period_end)`, sin asumir iguales políticas de elegibilidad.

La selección de meses regulares es un subconjunto descriptivo conservador, no una reproducción de la muestra publicada ni una validación predictiva. Fechas finales y banderas retrospectivas se usan para auditar cobertura/selección; no se exportan como predictores. No adjudicar churn desde códigos ambiguos ni entrenar sin resolver target/censura en el módulo Retention.
