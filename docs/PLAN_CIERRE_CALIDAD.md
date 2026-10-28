# Plan de cierre de calidad — DataTrust API

Fecha de inicio: 27 de octubre de 2026.

Objetivo: convertir v0.2.1 en un candidato v0.3.0 de portafolio local, reproducible y
fácil de evaluar, sin presentarlo como producto empresarial ni publicarlo.

## Línea base auditada

| Evidencia | Resultado inicial |
|---|---|
| Fuente / FastAPI / `pyproject.toml` | 0.2.1 / 0.2.1 / 0.2.1 |
| Metadata editable existente | 0.1.1 — inconsistente |
| Python / SQLite | 3.12.14 / 3.53.1 |
| Dependencias principales | FastAPI 0.162.0, Starlette 1.10.0, Pydantic 2.14.1, Uvicorn 0.54.0, pytest 9.1.1, HTTPX 0.28.1 |
| `pip check` | correcto, sin requisitos rotos |
| Recolección | 105 pruebas en 0.69 s |
| Suite | 105 aprobadas, 1 advertencia, 6.60 s |
| Compilación / JavaScript | código 0 / código 0 con Node 24.22.1 |
| Smoke HTTP loopback | correcto; carga 201, rutas 200/404 y temporal eliminado |
| Inventario aproximado | 68 archivos, 262.516 bytes y 4.502 líneas fuera de entornos/backups |
| Git | `main`, sin commits, HEAD, remotos ni publicación; árbol sin seguimiento |

La advertencia inicial es `StarletteDeprecationWarning`: Starlette 1.10.0 usa
HTTPX 0.28.1 como fallback porque `httpx2` no está instalado. Python 3.11,
Docker y CI remota no están disponibles/probados en esta máquina.

## Preservación

- Snapshot: `.local-backups/datatrust-v0.2.1-before-quality-close-20261027.zip`.
- SHA-256: `B7830A34CF7700A9AE09BE8C09022D1F70EE57FDF3B80C4C159123BB0C8DD6C3`.
- Contenido: 89 entradas; cero entradas prohibidas al revisar con `tar -tf`.
- Exclusiones: Git, entornos, backups, bases, cachés, logs, secretos,
  certificados y metadata generada.

## Inventario y complejidad observada

La separación principal sigue siendo pequeña y comprensible: HTTP en
`main.py` (227 líneas), validación en `validator.py` (194), perfiles en
`profiles.py` (263) y persistencia en `store.py`. Las pruebas más grandes son
las de límites T-105. No se detectó una razón para reescribir el stack.

Duplicación aceptable: fixtures sintéticos `sample_run`/`valid_row` aparecen en
varios módulos de prueba para mantenerlos independientes. La documentación
histórica repite resultados deliberadamente, pero `VERIFICACION.md` todavía
contenía al iniciar una referencia introductoria a fuente 0.2.0 que contradecía
el estado 0.2.1; quedó corregida. El workflow real es `tests.yml`, no `ci.yml`.

## Tablero de hitos

| Hito | Prioridad | Estado | Condición de aceptación | Evidencia prevista |
|---|---|---|---|---|
| Preservación y baseline | P0 | COMPLETADO | Snapshot verificable y suite inicial medida | hash, Git, 105/105 y smoke |
| Instalación limpia Python 3.12 | P0 | COMPLETADO | venv descartable, metadata correcta, `pip check`, suite e HTTP verdes | 0.3.0 coherente; 109 pruebas y smoke |
| HTTPX/TestClient | P0 | COMPLETADO LOCAL 3.12 | Migrar a `httpx2` solo si documentación, instalación y suite lo validan; si no, bloqueo explícito | httpx2 2.16.0, sin warning |
| Backend y seguridad local | P0 | COMPLETADO | Cero 500 reproducible en entradas/locks esperados; regresión por defecto corregido | regresiones y 503 controlado |
| UX profesional y accesible | P1 | COMPLETADO | Flujo real completo, estados claros y sin overflow en 360/390/768/1366 | E2E, teclado y capturas observadas |
| Smoke, benchmark y CI local | P1 | COMPLETADO LOCAL | HTTP loopback, benchmark 100/1.000/10.000 y comandos equivalentes de CI | outputs ejecutados |
| Documentación de portafolio | P1 | COMPLETADO | README ES/EN, demo de reclutador, arquitectura, seguridad e informe coherentes | enlaces y contratos revisados |
| Docker / Python 3.11 / CI remota | P2 | BLOQUEADO | Ejecutar solo si las herramientas/plataforma existen | razón objetiva o evidencia real |
| ML experimental | P2 | NO EJECUTADO | Solo ejecutar con dependencia/dataset/métricas defendibles; si no, NO EJECUTADO | diseño existente; falta dataset válido |
| Cierre final | P0/P1 | COMPLETADO | Suite completa, E2E, riesgos, archivos e informe de aceptación | `INFORME_CIERRE_CALIDAD_CODEX.md` |

## Criterio de versión

Se adoptó 0.3.0 únicamente después del rediseño visible, el E2E responsive, la
instalación limpia y la coherencia de paquete/API/documentación/pruebas. Sigue
siendo una demo local, no una declaración de madurez productiva.

## Orden de ejecución

1. Resolver reproducibilidad y metadata en un entorno Python 3.12 limpio.
2. Escribir regresiones para defectos backend observables y corregirlos con
   cambios pequeños.
3. Refinar la UI existente y comprobarla con navegador real.
4. Ejecutar smoke, benchmark, comandos CI locales y revisión de artefactos.
5. Alinear documentación y cerrar el informe sin ocultar bloqueos.
