# Prompt 01 — Mejoras guiadas de calidad de datos

Sigue `AGENTS.md`. Revisa y ejecuta tests de referencia. Implementa una mejora a la vez: primero identifica casos límite en CSV, luego agrega pruebas que FALLEN para esos casos, después aplica la corrección mínima. No cambies reglas de negocio sin documentarlo.

Foco: headers con espacios y columnas extra, truncación, errores de lectura de CSV, límites de filas, rendimientos y validación de email/fechas/importes. Documenta los casos que NO pueden validarse correctamente sin contexto empresarial.

Al terminar, ejecuta `python -m pytest -q`, entrega resultados reales, explica cambios línea por línea y pídeme resolver un caso nuevo para aprender.
