# Cómo continuar este proyecto en Codex

1. Descarga el ZIP, descomprímelo y abre **esa carpeta** como proyecto de trabajo en Codex.
2. Lee `README.md` y `docs/PRD.md` para entender el problema. No compartas información personal real en archivos de prueba.
3. Pega íntegro `prompts/00_AUDITORIA_CODEX.md` en Codex. Su primera tarea es **auditar lo que ya existe**, no volver a crear el proyecto.
4. Revisa sus conclusiones y pídele explicar el flujo completo: HTTP -> lectura CSV -> validaciones -> SQLite -> respuesta JSON.
5. Usa `prompts/01_MEJORAR_VALIDACIONES.md` para una primera mejora guiada con tests.
6. Continúa con `prompts/02_REPORTES_CSV.md` cuando la versión actual esté comprendida y estable.
7. Publica el repositorio cuando tengas pruebas y documentación coherentes. En GitHub, verifica que el CI se ejecute correctamente; no pegues tokens ni claves.

## Ejercicio de aprendizaje antes de la siguiente fase
- Explica qué hace `POST /api/v1/runs`.
- ¿Qué diferencia hay entre `422`, `413` y `415` en nuestra API?
- ¿Por qué decidimos no guardar el contenido original del CSV?
- ¿Para qué sirve una base de datos y qué es una clave foránea?
- ¿Qué cambia si el archivo contiene dos filas con el mismo `order_id`?

## Propuesta de mensaje para una publicación técnica (solo cuando se verifique)
"Construí y documenté un prototipo local de control de calidad de datos con Python/FastAPI y SQLite. Procesa CSV sintéticos, aplica reglas deterministas, registra incidencias y cuenta con pruebas automatizadas. Estoy mejorando su capacidad para configurar reglas y generar reportes. Código y limitaciones: [enlace real al repositorio]."
