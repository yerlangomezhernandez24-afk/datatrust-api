# Informe de cierre de calidad — DataTrust API v0.3.0

Fecha: 27 de octubre de 2026. Estado: **candidato de portafolio y demo local verificada; no apto para producción ni exposición pública**.

## A. Estado inicial auditado

- Repositorio trabajado: `<RUTA_LOCAL>\DataTrust_API_Starter`.
- Inicio: fuente/FastAPI/`pyproject` 0.2.1; metadata editable 0.1.1.
- Línea base: 105 pruebas recolectadas, 105 aprobadas y 1 warning en 6,60 s.
- Git local en `main`, sin `HEAD`, commits ni remotos; todo el proyecto estaba sin seguimiento. No se publicó, configuró remoto ni creó commit.
- Snapshot previo: `.local-backups/datatrust-v0.2.1-before-quality-close-20261027.zip`, SHA-256 `B7830A34CF7700A9AE09BE8C09022D1F70EE57FDF3B80C4C159123BB0C8DD6C3`, 89 entradas y cero entradas prohibidas.
- Inventario inicial fuera de venv/backups: 68 archivos, 262.516 bytes y 4.502 líneas aproximadas. Se preservó la arquitectura existente; el crecimiento del cierre se concentró en evidencia, documentación y UI.

## B. Hitos y evidencia

| Hito | Estado | Evidencia |
|---|---|---|
| Preservación/baseline | COMPLETADO | snapshot/hash, inventario, 105/105 |
| Instalación limpia 3.12 | COMPLETADO | metadata 0.3.0, `pip check`, 109/109, smoke |
| T-109 httpx2 | COMPLETADO LOCAL | httpx2 2.16.0, suite sin warning |
| Backend/seguridad local | COMPLETADO | regresiones rojas→verdes, 503 y headers |
| UX/E2E | COMPLETADO | flujo, 422, descarga, teclado y cuatro viewports |
| Benchmark/CI local | COMPLETADO LOCAL | benchmark repetido, comandos del workflow verdes |
| Python 3.11 | NO PROBADO | intérprete no instalado |
| Docker | NO PROBADO | comando no disponible; no se instaló globalmente |
| GitHub Actions remoto | NO EJECUTADO | no existe remoto/publicación |
| ML | NO EJECUTADO | sin dataset etiquetado que pruebe valor incremental |

## C. Archivos modificados o creados

| Grupo | Archivos | Razón |
|---|---|---|
| Paquete/dependencias | `pyproject.toml`, `constraints/verified-py312.txt`, `src/datatrust_api/__init__.py` | versión 0.3.0, httpx2, assets y snapshot probado |
| Backend | `main.py`, `store.py`, `profiles.py`, `csv_export.py` | headers, locks/close, mensajes no reflejados y fórmula segura |
| Frontend | `static/index.html`, `styles.css`, `app.js`, `sample-orders.csv`, `favicon.svg` | rediseño responsive, estados, ejemplo y asset local |
| Smoke/ejemplos | `scripts/smoke_http_e2e.py`, `examples/orders_invalid_structure.csv` | 413/headers y error reproducible |
| Pruebas | `test_api.py`, `test_export.py`, `test_profiles.py`, `test_sqlite_concurrency.py`, `test_dashboard.py`, `test_http_smoke.py` | regresiones y contrato UI/HTTP |
| Higiene | `.gitignore`, `.dockerignore` | venvs descartables y artefactos fuera de Git |
| Producto | `README.md`, `README.en.md`, `CHANGELOG.md`, `SECURITY.md` | alcance, instalación y presentación coherentes |
| Evidencia/diseño | `PLAN_CIERRE_CALIDAD.md`, `PROGRESO_CODEX.md`, `VERIFICACION.md`, `DEPENDENCIES.md`, `BENCHMARK.md`, `PRD.md`, `ARCHITECTURE.md`, `BACKLOG.md` | decisiones y resultados actuales |
| Entrega | `DEMO_RECLUTADOR.md`, este informe | recorrido y auditoría final |

Los informes anteriores se conservaron como historia; no se reescribieron para aparentar que sus resultados eran actuales.

## D. API y frontend que funcionan

Rutas verificadas: `/`, `/health`, `/api/v1/profiles`, `POST /api/v1/runs`, listado/detalle, incidencias paginadas y exportación CSV. El POST acepta CSV UTF-8 permitido, aplica límites separados de request/archivo/filas, valida con el perfil seleccionado en threadpool y persiste resumen/incidencias en una transacción.

El dashboard consulta la API real, muestra salud, perfiles, carga, métricas, historial, detalle, paginación y descarga. Usa `textContent`, no `innerHTML` ni almacenamiento web. El flujo final produjo 4/1/3/3 con `orders_usd_v1`; el error de columnas faltantes devolvió 422 accesible y no creó una ejecución. El nombre mostrado/persistido fue un UUID técnico `.csv`, no el original.

## E. Pruebas ejecutadas

Comandos principales:

```powershell
.\.venv-verify-py312\Scripts\python.exe scripts\check_version.py --installed
.\.venv-verify-py312\Scripts\python.exe -m pip check
.\.venv-verify-py312\Scripts\python.exe -m compileall -q src tests scripts
.\.venv-verify-py312\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv-verify-py312\Scripts\python.exe scripts\smoke_http_e2e.py
node --check src\datatrust_api\static\app.js
.\.venv\Scripts\python.exe scripts\benchmark_validation.py --rows 100 1000 10000 --repeats 5
```

Resultados observados:

- Python 3.12.14, SQLite 3.53.1, Node 24.22.1.
- 109 pruebas recolectadas en 0,91 s; ejecución limpia final: **109 aprobadas, 0 fallidas, 0 warnings, 7,21 s**.
- `compileall`, `pip check`, sintaxis JavaScript y check de versión: código 0.
- Smoke real: carga 201; rutas normales 200; desconocido 404; sobredimensionado 413 sin persistencia; headers presentes; BOM presente; DB temporal eliminada.
- Navegador integrado: E2E real con carga, error 422, descarga, lista vacía inicial, estado de éxito, teclado y layouts 360×800, 390×844, 768×1024, 1366×768. Consola final limpia.
- No se ejecutó una auditoría WCAG formal ni Playwright como dependencia del proyecto; la automatización fue la capacidad de navegador disponible.
- Docker, Python 3.11 y CI remota: no ejecutados por razones de la tabla B.

## F. Datos, seguridad y riesgos residuales

| Severidad | Riesgo | Mitigación o siguiente decisión |
|---|---|---|
| Alta si se expone | sin autenticación, autorización, tenants, TLS ni mitigación de abuso | mantener loopback; diseñar identidad/aislamiento antes de Internet |
| Alta si hay datos reales | sin retención/borrado verificable ni cifrado en reposo | solo datos sintéticos; política y modelo de amenazas antes de piloto |
| Media | SQLite tiene una escritura efectiva y un worker soportado | 503/timeout actual; medir WAL o migrar para concurrencia real |
| Media | proxy/servidor puede bufferizar un chunk antes del límite ASGI | repetir límites en infraestructura futura |
| Media | identificadores técnicos aún pueden correlacionarse | no llamarlos anónimos; definir retención y acceso |
| Baja | dependencia/CI 3.11 no revalidada | ejecutar matriz en entorno controlado cuando exista remoto |
| Baja | Dockerfile no construido | build/run local antes de citar Docker como verificado |

No hubo pentest, SAST remoto ni revisión externa. Los headers defensivos no convierten la demo en una aplicación pública segura.

## G. Razonamiento UX

La pantalla anterior funcionaba pero comunicaba poco valor y tenía jerarquía limitada. Se incorporó un sistema de tokens, hero sobrio, etiqueta Demo local, salud real, recorrido de tres pasos, muestra descargable, privacidad, métricas, ayuda de errores y footer documental. Se evitó CDN, gradientes decorativos y contenido simulado.

Se corrigieron overflow, tracks mínimos, paginación por `limit+1`, conservación de perfil, limpieza exclusiva del archivo, estados busy/error, singular/plural, favicon y tamaños táctiles. El DOM confirmó una sola instancia de cada sección; una captura full-page mostró artefactos de costura del navegador y no se trató como duplicación real. Las capturas reales se mostraron durante la verificación, pero no se guardaron en `docs/assets` porque la superficie no ofrecía exportación estable al filesystem.

## H. ML

**NO EJECUTADO.** No existe un dataset etiquetado independiente que permita comparar honestamente anomalías contra las reglas. La propuesta en `ML_EXPERIMENT_PROPOSAL.md` mantiene split, baseline, leakage y métricas como criterios futuros. No se añadió un modelo, endpoint ni porcentajes inventados.

## I. Empaquetado y warning

Una venv limpia instaló el proyecto editable con constraints. Fuente, paquete, FastAPI y metadata instalada reportaron 0.3.0. `httpx2` eliminó el `StarletteDeprecationWarning` sin filtros. El wheel final (30.724 bytes, SHA-256 `1571ADE4335212813E5BEC96F6AFF32D80015EA83DDE6753485AB31760B8989D`) se construyó e inspeccionó con perfiles, dashboard, favicon y CSV de muestra; el artefacto generado se eliminó después. El snapshot de constraints añade `colorama` y `opentelemetry-api`, transitivas observadas que faltaban en la lista anterior.

## J. Reproducción en Windows PowerShell

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -c constraints\verified-py312.txt -e ".[dev]"
python scripts\check_version.py --installed
python -m pytest -q -p no:cacheprovider
python -m uvicorn datatrust_api.main:app --host 127.0.0.1 --port 8000 --workers 1
```

Abrir `http://127.0.0.1:8000/`; usar `src/datatrust_api/static/sample-orders.csv`. Para limpiar **solo una DB sintética creada deliberadamente en la ruta predeterminada**, detener primero Uvicorn, verificar la ruta y luego:

```powershell
Get-Item -LiteralPath .\data\datatrust.sqlite3
Remove-Item -LiteralPath .\data\datatrust.sqlite3
```

No ejecutar esa limpieza si `DATATRUST_DB` apuntó a otro archivo o si la procedencia de los datos no es segura.

## K. Decisiones del titular

- Elegir identidad Git y decidir cuándo crear el primer commit.
- Elegir licencia; no existe `LICENSE` y no se asumió una.
- Decidir publicación GitHub, CI remota o recursos cloud; nada fue publicado.
- Instalar/verificar Python 3.11 y Docker solo si el titular lo autoriza.
- Aprobar un proyecto separado de seguridad/operaciones antes de cualquier despliegue público.

## L. Material de portafolio y siguiente paso

El recorrido, guion inglés, preguntas y texto honesto para CV están en `DEMO_RECLUTADOR.md`. Próximo hito recomendado: **v0.3.1 de reproducibilidad externa**, limitado a ejecutar Python 3.11, Docker y CI remota cuando existan las herramientas y el titular decida publicar. No añadir funciones hasta cerrar esa evidencia o validar necesidades con usuarios sintéticos.

## Aceptación final

| Check | Resultado |
|---|---|
| P0 integridad/backend sin 500 esperado reproducido | APROBADO |
| P0 instalación limpia y versión coherente 3.12 | APROBADO |
| P0 suite y smoke real | APROBADO |
| P1 demo visual funcional y responsive | APROBADO |
| P1 documentación ES/EN y recorrido | APROBADO |
| P1 empaquetado con assets | APROBADO |
| Python 3.11 | NO EJECUTADO — intérprete ausente |
| Docker build/run | NO EJECUTADO — Docker ausente |
| CI remota | NO EJECUTADO — sin remoto/publicación |
| Seguridad para Internet | FALLÓ POR DISEÑO — fuera de alcance; mantener local |
| ML con evidencia | NO EJECUTADO — datos insuficientes |

La suite verde prueba los contratos cubiertos en este entorno; no prueba ausencia universal de errores ni aptitud para producción.
