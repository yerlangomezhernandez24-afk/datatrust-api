# Propuesta experimental ML — no ejecutada

Estado v0.3.0: **NO IMPLEMENTADO; propuesta preparada**. El 27 de octubre de 2026 se revalidó `scikit-learn=False`. No se agregó una dependencia pesada solo para decorar el proyecto ni se inventaron métricas.

## Pregunta evaluable

¿Un `IsolationForest` local, entrenado con datos sintéticos reproducibles, detecta anomalías numéricas/de comportamiento que no cubren las reglas deterministas sin aumentar demasiado los falsos positivos?

## Diseño mínimo aceptable

- Generador sintético con semilla fija y etiquetas creadas antes del entrenamiento.
- Separación por grupos entre entrenamiento, validación y prueba para evitar leakage de pedidos casi idénticos.
- Features no sensibles y explicables: importe log-transformado, día de semana, frecuencia sintética por cliente/moneda y desviaciones respecto a patrones generados.
- Baseline determinista ejecutado sobre el mismo conjunto.
- Umbral elegido solo con validación; prueba final usada una vez.
- Métricas: matriz de confusión, precision, recall y F1 por clase, además del número de alertas.
- Registro de versión de datos, semilla, dependencias, modelo y umbral.

## Límites obligatorios

- Las predicciones serían alertas experimentales, nunca rechazos automáticos.
- No se usarían filas privadas ni se persistirían datos crudos.
- Sin etiquetas honestas no se publicarían precision/recall.
- El experimento no afirmaría adopción empresarial ni superioridad general.

Hasta ejecutar este protocolo con dependencias disponibles y resultados reales, no existe una función ML en el producto.

## Conclusión vigente en v0.3.0

**Todavía no hay evidencia de que ML aporte valor.** El validador acaba de adquirir límites de campo y reglas monetarias auditables; no existe un dataset etiquetado que permita medir anomalías adicionales frente a esa baseline. Un generador sintético diseñado por el mismo autor podría favorecer artificialmente al modelo. Por ello la decisión responsable es mantener este experimento aislado y pendiente, sin endpoint, modelo serializado ni afirmaciones de fraude/anomalías reales.
