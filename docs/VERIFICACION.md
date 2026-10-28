# Historial de verificación local — v0.1.1 a v1.0.0

Fecha de cierre actual: 27 de octubre de 2026.

Entorno actual: Windows 11 `10.0.26200`, Python 3.12.14, SQLite 3.53.1 y venvs limpias ignoradas para fuente/wheel.

Dependencias finales observadas: DataTrust API 1.0.0, FastAPI 0.162.0, Starlette 1.10.0, Pydantic 2.14.1, Uvicorn 0.54.0, python-multipart 0.0.32, pytest 9.1.1 y httpx2 2.16.0.

Los párrafos posteriores conservan evidencia histórica de los estados 0.1.x–0.3.0. La inconsistencia antigua de metadata y la advertencia HTTPX quedaron resueltas mediante instalaciones limpias; no deben interpretarse como estado final.

## Línea base v0.1.1 antes de los cambios

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Resultado observado al ejecutar con acceso normal a los temporales del proyecto:

```text
............................                                             [100%]
28 passed, 1 warning in 1.37s
```

Un primer intento dentro del sandbox produjo `17 passed, 11 errors`: los once errores eran fallos de permisos al crear el directorio temporal de pytest y `.pytest_cache`, no fallos de la aplicación. Se repitió la misma orden con acceso autorizado y se obtuvo la línea base anterior.

## Comparación con la estabilización v0.1.1

La evidencia anterior registraba tres estados:

1. suite original: 21 pruebas aprobadas;
2. regresiones escritas antes de corregir v0.1.1: 8 fallidas y 20 aprobadas (28 en total);
3. suite final v0.1.1: las mismas 28 aprobadas.

Entre el estado rojo de 28 y el verde de 28 no se eliminó, sustituyó ni parametrizó una prueba. Frente a las 21 originales se añadieron siete casos recolectados (cinco de API y dos de almacenamiento) y se reforzó una prueba existente de paginación; por eso se observaron ocho fallos antes de corregir. La parametrización histórica `test_bad_values` conservó sus siete variantes.

En v0.1.2 se preservaron esas 28 pruebas y se añadieron 25 casos recolectados: 21 en `test_t105.py` y cuatro en `test_sqlite_concurrency.py`. Parte de ese crecimiento procede de parametrizaciones explícitas para filas, importes y fechas; no sustituye pruebas anteriores.

## Ciclo rojo de v0.1.2

Primera ejecución focalizada de T-105 y concurrencia:

```text
2 failed, 21 passed, 1 warning in 2.22s
```

Los fallos reprodujeron que `Café` (NFC) y `Cafe\u0301` (NFD) no se reconocían como el mismo `order_id`, y que un email con NUL se aceptaba como válido.

Una regresión adicional mantuvo un bloqueo `BEGIN IMMEDIATE` hasta agotar un timeout corto de prueba. Antes de la corrección produjo una respuesta HTTP 500:

```text
1 failed, 1 warning in 0.88s
AssertionError: Internal Server Error; assert 500 == 503
```

## Resultado focalizado final v0.1.2

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_t105.py tests/test_sqlite_concurrency.py -p no:cacheprovider
```

```text
.........................                                                [100%]
25 passed, 1 warning in 3.24s
```

## Resultado completo final v0.1.2

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
```

```text
.....................................................                    [100%]
53 passed, 1 warning in 3.79s
```

La advertencia es `StarletteDeprecationWarning` por la integración actual de `TestClient` con HTTPX. No invalida estas pruebas, pero los rangos amplios de dependencias siguen siendo un riesgo de reproducibilidad.

## Cobertura comprobada en v0.1.2

- CSV válido de exactamente 2.097.152 bytes -> HTTP 201; el mismo archivo más un byte -> HTTP 413 y sin ejecución parcial.
- El cuerpo multipart del caso aceptado es mayor de 2 MiB; el límite corresponde al archivo, no al sobre HTTP.
- 10.000 filas -> HTTP 201; 10.001 -> HTTP 422 y sin persistencia parcial.
- UTF-8, BOM, Unicode válido y una muestra CP-1252 inválida.
- Columnas extra, duplicadas, obligatoria sustituida por nombre inesperado y conteo de celdas incorrecto.
- CSV mal formado, fechas imposibles, importes no finitos/no positivos y valores finitos de magnitud/escala extremas.
- Páginas intermedias, última página, página vacía y límites de `limit`/`offset` con datos reales.
- Ausencia del nombre original, valores de filas y fórmulas en respuestas e `iterdump()` de SQLite.
- Smoke de seis escrituras coordinadas por barrera sin pérdida de ejecuciones/incidencias, espera por un lock controlado, éxito tras liberarlo y HTTP 503 sin fila parcial cuando se agota el timeout. La barrera coordina el arranque, pero no demuestra por sí sola que las seis transacciones poseyeran el lock simultáneamente.

La muestra `examples/orders_with_issues.csv` continúa representando **6 filas totales, 2 válidas, 4 inválidas y 5 incidencias**. Ver `examples/sample_validation_result.json`; todos los datos son ficticios.

## v0.1.3 — límite ASGI y concurrencia

Las pruebas nuevas comenzaron en rojo por ausencia del middleware. La primera implementación produjo tres 400 en requests fragmentados porque Starlette capturaba la señal del canal `receive`; se corrigió suprimiendo esa respuesta interna y emitiendo el 413 exterior.

```text
tests/test_request_limits.py: 6 passed, 1 warning in 0.80s
request limits + SQLite: 11 passed, 1 warning in 1.36s
suite completa v0.1.3: 60 passed, 1 warning in 3.38s
```

Se comprobó límite exacto del middleware, rechazo al siguiente byte, cabecera alta sin leer el body, chunks reales sin cabecera/con cabecera falsa, ausencia de persistencia, lector/escritor y locks de escritura.

## v0.2.0 — perfiles, exportación y dashboard

Resultados focalizados observados:

```text
T-102 exportación: 3 passed, 1 warning in 1.07s
T-101 + validator + API: 34 passed, 1 warning in 1.42s
dashboard: 2 passed, 1 warning in 1.01s
```

Resultado completo intermedio antes del cierre documental:

```text
74 passed, 1 warning in 4.55s
```

Resultado completo final después de revisar código, documentación y árbol Git:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
```

```text
74 passed, 1 warning in 4.23s
```

Comprobaciones adicionales:

- `python -m compileall -q src tests scripts`: código 0, sin salida.
- `python -m pip check`: `No broken requirements found.`
- `node --check src/datatrust_api/static/app.js`: código 0 con Node v24.22.1.
- Benchmark T-104 ejecutado; resultados completos en `BENCHMARK.md`.
- `docker version`: comando no encontrado. Docker build/run NO EJECUTADOS.
- Workflow actualizado a Python 3.11/3.12, pero GitHub Actions remoto NO EJECUTADO.
- `scikit-learn` no instalado; ML NO EJECUTADO y solo documentado como propuesta.

## Límites de esta evidencia final

- El límite ASGI corta antes del parser de aplicación, pero un servidor/proxy puede recibir o bufferizar un chunk antes de entregarlo; un despliegue futuro necesitaría un límite coherente adicional.
- Las pruebas SQLite son locales y controladas. No son un benchmark ni prueban varios procesos, filesystem de red o carga sostenida. No se activó WAL.
- Se observó mediante diagnóstico el límite implícito de `csv.field_size_limit()` (131.072 caracteres en este entorno); falta convertirlo en contrato y mensaje específico.
- Un `order_id` compuesto solo por caracteres de formato invisibles todavía cuenta como no vacío. Su política se dejó para T-108 para no introducir silenciosamente una gramática nueva de identificadores.
- La gramática de `Decimal` todavía admite formas como notación científica y no define precisión/escala de negocio. Se documenta para T-108 en vez de cambiar el contrato sin decisión de producto.
- No se ejecutaron GitHub Actions remotas, construcción Docker, navegador E2E, pentest, despliegue, evaluación formal de accesibilidad ni pruebas con usuarios reales. El benchmark mide solo la función pura, no el servicio completo.

## Continuación v0.2.1 — 27 de octubre de 2026

### Línea base revalidada

```text
74 passed, 1 warning in 5.62s
74 tests collected in 0.98s
```

Los 74 casos procedían de 53 funciones `test_*`; siete usos de `pytest.mark.parametrize` añadían 21 variantes. Esto no contradice los hitos históricos de 28/53: son ampliaciones acumulativas ya explicadas arriba.

### T-108: política de datos

Las regresiones nuevas comenzaron con `12 failed, 6 passed, 1 warning in 1.66s`. Reprodujeron importes con signo positivo/exponente/escala/rango aceptados, límites ausentes, controles invisibles en identificadores y el error opaco del parser ante 140.000 caracteres.

Después de implementar perfiles con límites y política Decimal:

```text
pruebas focalizadas: 77 passed, 1 warning in 3.17s
suite completa:      97 passed, 1 warning in 4.95s
```

El cambio de contrato está documentado: dos importes extremos finitos que antes se aceptaban ahora producen `VALUE_TOO_LONG`. No se eliminó la prueba; se actualizó su expectativa conforme a la política previa al código.

### SQLite y recuperación

- Pruebas iniciales: dos errores de colección por módulos aún inexistentes.
- Focalizadas finales de mantenimiento/concurrencia: `13 passed, 1 warning in 1.81s`.
- Se añadió después `foreign_key_check`; la suite creció un caso.
- Smoke CLI real: check/backup/restore/check con integridad `ok`, destino nuevo y 6 páginas.
- Primer benchmark journal: código 1 porque conexiones del propio script quedaron abiertas y Windows bloqueó el temporal. Se corrigió; ese intento no produjo métricas válidas.
- Ejecución válida de 20 repeticiones: DELETE 0 commits/20 BUSY, mediana de intento 0,495750 ms; WAL 20 commits/0 BUSY, mediana 10,856050 ms; integridad `ok` y `synchronous=FULL`.
- Decisión: no activar WAL automáticamente; ver `SQLITE_OPERATIONS.md`.

Suite completa al cerrar esta fase:

```text
103 passed, 1 warning in 5.06s
```

### Dashboard, HTTP y navegador

- La primera prueba HTTP no recolectó porque faltaba el script; después falló por asumir casing exacto de `Content-Disposition` en `urllib`. Se normalizaron nombres de headers.
- Focalizadas finales: `3 passed, 1 warning in 2.30s`.
- `scripts/smoke_http_e2e.py`: health/dashboard/perfiles/listado/detalle/páginas/exportación 200, carga 201, desconocido 404, perfil USD, BOM presente y temporal eliminado.
- Navegador integrado con automatización Playwright: carga sintética real, perfil USD, métricas 6/0/6/9, tabla, historial, descarga y error 415.
- Error anunciado con `role=alert`/`aria-live=assertive`; foco visible con outline sólido de 2,4 px.
- A 390×844 se reprodujo overflow horizontal: workspace ~596 px. Tras `min-width:0`, `scrollWidth=375`, workspace 359,2 px y la página cupo en el viewport. Se restauró a 1280 px.
- Playwright no estaba instalado como paquete/comando; la automatización procedió de la herramienta de navegador ya disponible. No se instaló software.
- Servidor: solo `127.0.0.1:8765`, un worker, DB temporal eliminada y puerto cerrado.
- `node --check`: código 0.

Suite al cerrar la fase:

```text
104 passed, 1 warning in 6.64s
```

### Reproducibilidad y versión

- Fuente/`pyproject`/FastAPI: 0.2.1, check código 0.
- Metadata instalada: 0.1.1, check `--installed` código 1 esperado y documentado.
- La venv no contiene `setuptools`, `wheel`, `build` ni ruedas cacheadas; no se pudo regenerar offline la instalación editable.
- `compileall`, `pip check` y `node --check`: código 0; `pip check` sin dependencias rotas.
- Suite posterior al bump: `105 passed, 1 warning in 6.43s`.
- Python 3.12.14: EJECUTADO. Python 3.11: NO EJECUTADO/no disponible.
- Docker: NO EJECUTADO/no disponible. GitHub Actions: NO EJECUTADO/no se publicó.
- Ruff/Black/mypy/parser YAML: NO EJECUTADOS/no disponibles; no se ocultó esta limitación.
- ML: NO EJECUTADO; `scikit-learn=False`, sin dataset etiquetado ni métricas.

La advertencia única sigue siendo la transición de Starlette 1.10.0: intenta `httpx2>=2` y, al no existir, usa HTTPX 0.28.1. No se ocultó ni se instaló especulativamente.

### Cierre final v0.2.1

```text
105 passed, 1 warning in 6.34s
105 tests collected in 0.97s
```

`compileall`, `pip check`, `node --check` y el check de versión fuente terminaron con código 0. El backup conservó SHA-256 `0AE498F6631E41F935031549432D67C4CC5E19210C199B421E096D7A05164A5A`, permaneció ignorado y su contenido volvió a pasar el filtro de entradas prohibidas. No se encontraron `.env`, bases, claves o certificados residuales fuera de `.venv`/backup ignorados. Git continúa sin commits, identidad ni remotos.

## Cierre de calidad v0.3.0 — 27 de octubre de 2026

### Línea base y reproducción de defectos

- Línea base antes del cierre: 105 pruebas recolectadas en 0,69 s; 105 aprobadas y 1 warning en 6,60 s.
- Regresiones backend nuevas antes de corregir: 4 fallidas, 31 aprobadas y 1 warning. Reprodujeron falta de headers, fórmula tras controles, eco de perfil y HTTP 500 en lectura bloqueada.
- Después de las correcciones: 37 focalizadas aprobadas en 3,37 s.
- Favicon: la regresión produjo 1 fallo/1 aprobación por 404; tras añadir el asset local quedaron 2 aprobadas en 0,94 s.

### Entorno limpio y empaquetado

```text
check_version.py --installed:
pyproject=0.3.0
package=0.3.0
fastapi=0.3.0
installed_metadata=0.3.0

pip check: No broken requirements found.
recolección final: 109 tests collected in 0.91s
pytest limpio final: 109 passed in 7.21s
```

La venv se creó desde cero y se instaló con `pip install -c constraints/verified-py312.txt -e ".[dev]"`. La suite no emitió warnings. El wheel final `datatrust_api-0.3.0-py3-none-any.whl` de 30.724 bytes se construyó correctamente (SHA-256 `1571ADE4335212813E5BEC96F6AFF32D80015EA83DDE6753485AB31760B8989D`) y se inspeccionó: contenía perfiles, HTML, CSS, JavaScript, favicon y CSV sintético. `build/` estaba ignorado por Git y se eliminó después de conservar esta evidencia.

### Smoke HTTP final

Ejecutado con Uvicorn real, host `127.0.0.1`, un worker y base temporal:

```text
health/dashboard/profiles/list/detail/issues/export = 200
upload = 201
unknown_run = 404
oversized_upload = 413
oversized_upload_persisted = false
X-Content-Type-Options = nosniff
X-Frame-Options = DENY
export_has_bom = true
temporary_database_removed = true
```

### Navegador real

- Flujo sintético USD: 4 filas, 1 válida, 3 inválidas y 3 incidencias; perfil conservado, archivo limpiado, nombre técnico UUID y exportación descargada.
- Error estructural: 422 anunciado con `role=alert`; no creó una ejecución.
- Teclado: skip-link y marca tuvieron foco visible sólido de 2,4 px.
- Responsive: 360×800, 390×844, 768×1024 y 1366×768 sin overflow horizontal. Tracks cambiaron de una columna móvil a layout de dos columnas en escritorio.
- Cierre final del navegador: badge `API local activa · v0.3.0`, favicon 200 y consola sin warnings/errores.
- Las capturas se observaron mediante la herramienta integrada, pero esa superficie no ofreció exportación estable a `docs/assets`; no se inventaron archivos de captura.
- Ambos servidores de navegador se detuvieron, sus bases temporales se eliminaron y el puerto 8766 quedó sin listener.

### Benchmark y límites de plataforma

La segunda repetición del benchmark midió medianas 1,815/17,735/185,589 ms para 100/1.000/10.000 filas. Ver `BENCHMARK.md`; no es SLA.

- Python 3.12.14: EJECUTADO.
- Python 3.11: NO EJECUTADO; no instalado en el host.
- Docker build/run: NO EJECUTADO; comando no disponible.
- GitHub Actions remoto: NO EJECUTADO; no hay remoto ni publicación.
- ML: NO EJECUTADO; no hay dataset etiquetado que sustente valor incremental.

## Cierre de portafolio v1.0.0 — 27 de octubre de 2026

### Línea base y regresiones

- Baseline antes del cambio: 109 casos descubiertos en 1,48 s; `109 passed`
  sin warnings en 7,03 s.
- Las tres pruebas nuevas de demos fallaron primero por archivos/enlaces
  inexistentes. Tras incorporar los recursos, las focalizadas terminaron
  `5 passed in 1.12s`.
- Suite final de fuente: **113 passed, 0 failed, 0 warnings in 7.22s**;
  duración externa medida 8,24 s.

### Instalación limpia y wheel

```text
Python 3.12.14
pip 25.0.1
pyproject=package=fastapi=installed_metadata=1.0.0
pip check: No broken requirements found.
recolección final: 113 tests collected in 0.85s
venv limpia: 113 passed in 7.13s
compileall=0; node --check=0
```

El wheel final `datatrust_api-1.0.0-py3-none-any.whl` midió 32.718 bytes y
SHA-256 `D445445C631713F17B0C80A2994B26801E45CDC7151192C426743618D1DA2A3E`.
Se instaló en una segunda venv y el módulo se importó desde `site-packages`.
No faltó ningún recurso: HTML, CSS, JavaScript, SVG, dos perfiles y dos demos.
La validación instalada reprodujo 6/2/5 y 100/90/10 como
total/válidas/incidencias.

### Smoke HTTP instalado

El intérprete del wheel inició Uvicorn en loopback con un worker y base temporal:

```text
health/dashboard/profiles/list/detail/issues/export = 200
upload = 201; profile = orders_usd_v1
unknown_run = 404
oversized_upload = 413; persisted = false
export_has_bom = true
X-Content-Type-Options = nosniff; X-Frame-Options = DENY
temporary_database_removed = true
```

### Navegador real

- Viewports 360×800, 390×844, 768×1024 y 1366×768: sin overflow horizontal
  de página; controles mínimos medidos en 44 px.
- Demo 100: 100/90/10/10 visible, diez incidencias y evento de descarga recibido.
- Demo 6 en móvil: 6/2/4/5, cinco filas de tabla y dos ejecuciones en historial.
- Error estructural: 422 visible con `role=alert`; no creó una ejecución.
- Selector USD, skip-link por teclado y aclaración de tabla móvil verificados.
- Las capturas fueron reales y se mostraron en la sesión de Codex; no se
  persistieron archivos de imagen dependientes del escritorio.

### Rendimiento y SQLite

- Validador puro (5 repeticiones): medianas 1,697/16,832/177,815 ms para
  100/1.000/10.000 filas. No es SLA.
- Journal (10 repeticiones): DELETE 0 commits/10 BUSY, mediana 0,512150 ms;
  WAL 10 commits/0 BUSY, mediana 10,529400 ms; integridad `ok`.
- WAL permanece desactivado; un worker y journal predeterminado son el contrato.

### No verificado

- Python 3.11: intérprete no instalado.
- Docker: comando no disponible; Dockerfile solo inspeccionado.
- GitHub Actions: sin remoto/publicación, por lo que no existe ejecución remota.
- macOS/Linux y pentest externo: no ejecutados.
