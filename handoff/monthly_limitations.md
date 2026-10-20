# Límites de la admisión mensual

Tres gimnasios históricos, selección propia de meses regulares; no representa automáticamente otros
gimnasios, Optimo, la cohorte publicada completa ni la población actual. Los endpoints/flags son
retrospectivos y pueden incorporar información posterior al corte; condicionan elegibilidad y no se
admiten como predictores. No hay reloj de ingesta ni zona horaria comprobada. Ver
[adecuación de fuente](../docs/data_readiness.md) y [plan](../docs/project_plan.md).

Un conteo mensual no contiene fechas de visitas, horas, duración, aforo, acceso efectivo, cierres ni
razones de ausencia. Las rachas solo miden historia elegible visible; meses sin soporte no son cero.
Recencia positiva desconocida al inicio no se imputa. Contratos no regulares e historiales interrumpidos
no se analizan mediante estas ventanas. La composición cambia entre meses y las observaciones por
persona se repiten. No se estimó incertidumbre de muestreo, estabilidad de estados ni efecto de intervención.

Las políticas de Member Behavior y Retention son diferentes, aunque procedan del mismo archivo.
Identidad de fuente no otorga equivalencia de población o features. Lisboa y Mindweave no se unen
por persona. No se validan engagement, riesgo, churn contractual, acciones ni transferencia operacional.

Derechos de redistribución del ZIP/tabla/derivados individuales no establecidos; originales y filas
individuales quedan locales e ignorados por Git. El core entrega agregados. La publicación Kaggle
usa código autónomo y fuente primaria en almacenamiento temporal, sin adjuntar datos. MIT solo cubre
código/documentación originales OGDT. [Revisión de derechos](../docs/publication_review.md).
