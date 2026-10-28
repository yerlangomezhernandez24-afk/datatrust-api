# Plan maestro supervisable de Codex

Última actualización: 26 de octubre de 2026.

Este documento es el punto de entrada para reanudar el trabajo. Debe leerse junto con `CODEX_PROGRESS.md`. El proyecto continúa siendo una demostración local educativa, no un servicio listo para producción.

## Reglas de ejecución

- Conservar Python 3.11+, FastAPI y SQLite, y mantener separadas las capas HTTP, validación y almacenamiento.
- Escribir primero una regresión cuando exista un defecto reproducible; no debilitar pruebas.
- Trabajar solo con datos sintéticos, sin servicios pagados, claves, publicación, remotos Git ni despliegues públicos.
- Mantener una versión ejecutable al cerrar cada fase y registrar comandos/resultados reales.
- No afirmar CI remoto, Docker, benchmarks, seguridad o ML si no fueron ejecutados y medidos.

## Fases

| Fase | Prioridad | Estado | Criterio de aceptación |
|---|---|---|---|
| 0. Estado real y línea base | P0 | COMPLETADO | Git, intérprete, dependencias y suite actual documentados; plan/progreso creados. |
| A. T-105 pruebas avanzadas | P0 | COMPLETADO | 28 pruebas previas preservadas; límites, encoding, esquema, privacidad, fórmulas, paginación y SQLite cubiertos; suite verde final. |
| B. Robustez HTTP/SQLite/local | P0 | COMPLETADO | Cuerpo HTTP limitado antes del multipart mediante bytes recibidos; CSV conserva 2 MiB; fragmentación y cabeceras falsas probadas; política SQLite y Docker local honestamente documentados. |
| C1. T-102 exportación segura | P1 | COMPLETADO | Endpoint CSV versionado, neutro, completo y resistente a formula injection, con pruebas. |
| C2. T-101 perfiles JSON mínimos | P1 | COMPLETADO | `orders_v1` preservado; perfil USD local versionado y esquema estricto sin `eval` ni rutas arbitrarias. |
| C3. T-103 idempotencia | P1 opcional | BLOQUEADO POR DISEÑO | Política propuesta; no implementar antes de identidad, privacidad y retención. |
| D. Dashboard local real | P1 | COMPLETADO | UI ligera servida por FastAPI, conectada a carga/listado/detalle/paginación/exportación; prueba de integración. |
| E. Experimento ML | P2 opcional | NO EJECUTADO | Protocolo documentado; scikit-learn ausente y ninguna métrica/modelo inventado. |
| F. Calidad y entrega | P1 | COMPLETADO | CI 3.11/3.12 preparada, estrategia de dependencias, benchmark medido, Docker marcado no disponible, SECURITY, documentación ES/EN e informe final. |

## Decisiones actuales

1. T-105 ya existe en el árbol; se verificará y completará sin reescribirlo.
2. El límite de 2 MiB significa bytes del archivo CSV. El límite del request multipart es separado, configurable y se aplica antes del parser.
3. La defensa ASGI contará mensajes `http.request`; `Content-Length` será solo una optimización/rechazo temprano, nunca la única fuente de verdad.
4. SQLite mantiene una conexión por operación, transacciones cortas, `foreign_keys=ON`, timeout explícito y traducción de lock agotado a 503. WAL requiere evaluación antes de activarlo.
5. La exportación incluye únicamente incidencias ya persistidas; no reconstruye ni almacena filas originales y neutraliza todas las celdas.
6. Los perfiles son una lista local permitida y versionada. No se acepta código, JSON ni rutas aportadas por el cliente.
7. T-103 queda condicionado a una política que no revele historiales entre futuros usuarios ni debilite privacidad; su diseño está documentado sin atajo de implementación.
8. El cierre verificó 74 pruebas, `compileall`, `pip check` y sintaxis JavaScript. Docker, CI remoto, navegador E2E y ML permanecen declarados como no ejecutados.

## Orden de reanudación

1. Leer `docs/CODEX_PLAN_MAESTRO.md` y `docs/CODEX_PROGRESS.md`.
2. Ejecutar `git status --short --ignored` sin limpiar el árbol.
3. Ejecutar `.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider`.
4. Si la suite continúa verde, iniciar el hito v0.2.1 por T-109; después T-108 y T-107. No repetir fases COMPLETADAS.
