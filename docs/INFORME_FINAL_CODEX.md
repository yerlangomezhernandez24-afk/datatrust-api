# Informe final de ejecución Codex — DataTrust API v0.2.0

Fecha de cierre: 26 de octubre de 2026.

## 1. Resultado ejecutivo

DataTrust API queda como un prototipo local de portafolio funcional y verificable. El flujo completo permite elegir un perfil permitido, cargar un CSV, validarlo con reglas deterministas, consultar ejecuciones e incidencias paginadas y descargar todas las incidencias mediante una exportación CSV protegida. También existe un dashboard local conectado a esos endpoints.

La última ejecución completa produjo **74 pruebas aprobadas y una advertencia en 4,23 s**. No hubo pruebas omitidas ni fallidas. La advertencia corresponde a la transición de `Starlette TestClient` desde HTTPX hacia `httpx2`; se dejó visible y pendiente de una migración compatible.

El servicio sigue siendo una demostración educativa: no incorpora autenticación, autorización, tenants, cifrado en reposo, retención ni controles propios de un servicio público. Debe ejecutarse en loopback, con un worker y datos sintéticos.

## 2. Estado real al iniciar y al cerrar

Al comenzar el prompt maestro, el árbol ya incluía la estabilización v0.1.2/T-105, no solo v0.1.1. Se verificó una línea base real de `53 passed, 1 warning in 3.66s`; por ello no se repitieron ni sustituyeron las 25 pruebas avanzadas existentes.

El repositorio Git local existe en la rama `main`, pero no tiene commits ni `HEAD`. Tampoco tiene remotos ni identidad `user.name`/`user.email` local o global. Debido a ello no se inventaron credenciales ni se creó un commit. Como Git se inicializó después de existir los archivos, todo el proyecto aparece sin seguimiento; los artefactos generados (`.venv`, `egg-info`, `__pycache__`, bases, sidecars, cobertura, secretos y logs) están ignorados.

Para crear el primer commit en una sesión futura, el titular debe configurar su identidad real, revisar el árbol y ejecutar, por ejemplo:

```powershell
git config user.name "TU NOMBRE REAL"
git config user.email "TU CORREO REAL"
git add .
git status
git commit -m "release: DataTrust API v0.2.0 local"
```

No se configuró remoto, no se hizo `push`, no se publicó ni desplegó nada.

## 3. Funcionalidad implementada

### Robustez HTTP y SQLite

- Middleware ASGI que cuenta los chunks reales del cuerpo antes del parser multipart. `Content-Length` solo permite rechazo temprano; una cabecera ausente, inválida o falsamente baja no evita el conteo.
- Límites independientes: CSV de 2 MiB y request multipart de 2 MiB + 64 KiB por defecto, configurable mediante `DATATRUST_MAX_REQUEST_BYTES`.
- Rechazo 413 sin persistencia parcial cuando el archivo o el request excede su límite.
- Conexión SQLite por operación, `foreign_keys=ON`, timeout explícito de cinco segundos, transacciones cortas, rollback y cierre garantizado.
- Conversión de `SQLITE_BUSY/LOCKED` agotado a HTTP 503 con `Retry-After: 1`, sin fila parcial.
- Un solo worker y filesystem local como política soportada. No se activó WAL sin evaluar recuperación y filesystems.

### Perfiles T-101

- Registro local y permitido de `orders_v1` y `orders_usd_v1`.
- JSON versionado con claves, tipos, referencias, ids y claves duplicadas validados estrictamente.
- Operadores permitidos: obligatoriedad, unicidad, email básico, decimal positivo finito, enumeración y fecha ISO.
- Sin `eval`, código dinámico, rutas aportadas por el cliente ni perfiles subidos.

### Exportación T-102

- Streaming de todas las incidencias con cursor SQLite y lotes de 500, sin el límite de 100 del detalle.
- UTF-8 con BOM, nombre neutral `validation-issues.csv` y biblioteca `csv` estándar.
- Neutralización de cada celda que, después de whitespace inicial, comience por `=`, `+`, `-` o `@`.
- No se reconstruyen ni exportan las filas originales.

### Dashboard T-201

- HTML, CSS y JavaScript locales servidos por FastAPI, sin CDN ni cuenta externa.
- Carga CSV, elección de perfil, estados de carga/error/vacío, métricas, historial, selección, paginación y descarga.
- Uso de `textContent` para datos dinámicos y CSP básica en el documento principal.

### Calidad y evidencia

- Matriz GitHub Actions preparada para Python 3.11 y 3.12.
- Snapshot exacto de dependencias observadas en Python 3.12.
- Dockerfile con usuario no root, volumen escribible y un worker.
- Benchmark reproducible del validador puro.
- Documentos de seguridad, perfiles, arquitectura, producto, verificación, plan y progreso.

## 4. Endpoints y rutas actuales

| Método | Ruta | Función |
|---|---|---|
| GET | `/` | Dashboard local |
| GET | `/static/*` | Assets locales del dashboard |
| GET | `/health` | Estado del proceso y versión |
| GET | `/api/v1/profiles` | Catálogo de perfiles permitidos |
| POST | `/api/v1/runs?profile=orders_v1` | Cargar y validar CSV |
| GET | `/api/v1/runs` | Listar ejecuciones con paginación |
| GET | `/api/v1/runs/{run_id}` | Resumen y primeras 100 incidencias |
| GET | `/api/v1/runs/{run_id}/issues` | Incidencias paginadas |
| GET | `/api/v1/runs/{run_id}/issues.csv` | Exportación completa protegida |

## 5. Pruebas creadas y defectos corregidos

La suite pasó de 53 a 74 casos recolectados. La ampliación cubre:

- request ASGI exacto, byte adicional, chunks fragmentados, cabecera ausente/falsa y rechazo temprano;
- lector/escritor SQLite coordinado, además de escritores y locks ya cubiertos;
- exportación de 105 incidencias frente a 100 del detalle, fórmulas, comillas, comas, Unicode y saltos;
- perfiles predeterminado/USD, ids desconocidos, simulación de traversal, documentos inválidos y claves JSON repetidas;
- assets y flujo backend completo utilizado por el dashboard.

Los defectos reproducidos y corregidos durante la secuencia v0.1.1–v0.2.0 fueron:

1. sufijos disfrazados tras nombres largos;
2. offset fuera del rango entero de SQLite;
3. conexiones no cerradas explícitamente;
4. configuración `:memory:` incompatible con conexión por operación;
5. exposición del nombre original del archivo;
6. trabajo síncrono dentro del endpoint async;
7. duplicados Unicode NFC/NFD no equivalentes;
8. caracteres de control/formato aceptados en email;
9. lock SQLite agotado convertido en 500;
10. falta de límite previo al parser multipart;
11. primera versión del middleware convertida por Starlette en 400 en requests fragmentados;
12. exportación limitada/inexistente y riesgo de formula injection;
13. perfil fijo sin catálogo seguro;
14. ausencia de una interfaz local conectada.

No se debilitó ninguna prueba existente para obtener verde.

## 6. Evidencia ejecutada

Entorno observado: Windows 11, Python 3.12.14, SQLite 3.53.1, FastAPI 0.162.0, Starlette 1.10.0, Pydantic 2.14.1, Uvicorn 0.54.0, python-multipart 0.0.32, pytest 9.1.1, HTTPX 0.28.1 y Node v24.22.1.

| Comprobación | Resultado real |
|---|---|
| Línea base del prompt maestro | `53 passed, 1 warning in 3.66s` |
| Suite final | `74 passed, 1 warning in 4.23s` |
| `python -m compileall -q src tests scripts` | código 0, sin salida |
| `python -m pip check` | `No broken requirements found.` |
| `node --check src/datatrust_api/static/app.js` | código 0 |
| Docker build/run | **NO EJECUTADO**: `docker` no está instalado |
| GitHub Actions remoto | **NO EJECUTADO**: no se publicó el repositorio |
| Navegador E2E/Playwright | **NO EJECUTADO**; integración equivalente de API/assets aprobada |
| ML | **NO EJECUTADO**: scikit-learn ausente; solo propuesta científica |

La instalación editable generada todavía informa 0.1.1 porque el entorno carece de `setuptools.build_meta`; el intento sin red de refrescarla falló. La fuente, `pyproject.toml`, `/health` y OpenAPI declaran 0.2.0. No se descargó una dependencia solo para corregir metadatos generados.

### Benchmark T-104 medido

Comando:

```powershell
.\.venv\Scripts\python.exe scripts\benchmark_validation.py --rows 100 1000 10000 --repeats 5
```

Equipo observado: Intel64 Family 6 Model 142 Stepping 12, 8 CPU lógicas, Windows 11 y Python 3.12.14.

| Filas | Bytes | Mínimo | Mediana | Máximo | Filas/s sobre mediana |
|---:|---:|---:|---:|---:|---:|
| 100 | 5.424 | 0,862 ms | 0,875 ms | 0,890 ms | 114.311,8 |
| 1.000 | 56.724 | 8,098 ms | 9,163 ms | 9,934 ms | 109.128,6 |
| 10.000 | 596.724 | 85,402 ms | 87,787 ms | 92,872 ms | 113.912,0 |

Estos números miden la función pura de validación, no HTTP, multipart, SQLite ni usuarios concurrentes. La metodología completa está en `BENCHMARK.md`.

## 7. Archivos creados o modificados

### Aplicación y configuración

- `src/datatrust_api/main.py`, `store.py`, `validator.py`, `models.py`, `__init__.py`.
- `src/datatrust_api/csv_export.py`, `profiles.py`.
- `src/datatrust_api/profile_data/orders_v1.json`, `orders_usd_v1.json`.
- `src/datatrust_api/static/index.html`, `app.js`, `styles.css`.
- `pyproject.toml`, `.gitignore`, `.dockerignore`, `Dockerfile`.
- `.github/workflows/tests.yml`, `constraints/verified-py312.txt`.
- `scripts/benchmark_validation.py`.

### Pruebas

- `tests/test_api.py`, `test_store.py`, `test_validator.py`.
- `tests/test_t105.py`, `test_sqlite_concurrency.py`, `test_request_limits.py`.
- `tests/test_export.py`, `test_profiles.py`, `test_dashboard.py`.

### Documentación

- `README.md`, `README.en.md`, `SECURITY.md`, `CHANGELOG.md`.
- `docs/PRD.md`, `ARCHITECTURE.md`, `BACKLOG.md`, `VERIFICACION.md`.
- `docs/PROFILES.md`, `BENCHMARK.md`, `IDEMPOTENCY_DESIGN.md`, `ML_EXPERIMENT_PROPOSAL.md`.
- `docs/CODEX_PLAN_MAESTRO.md`, `CODEX_PROGRESS.md` y este informe.

## 8. Decisiones y trabajo omitido

- **T-103/idempotencia:** no se implementó un hash global. Sin identidad/tenant y retención podría revelar que otro usuario ya cargó un archivo. `IDEMPOTENCY_DESIGN.md` define una solución futura por tenant y transacción.
- **WAL:** no se activó. Cambia comportamiento persistente y debe verificarse recuperación, backups y filesystem antes de aplicarlo.
- **ML:** no se añadió una dependencia pesada ni un modelo decorativo. Falta una evaluación con etiquetas, separación correcta y baseline; `ML_EXPERIMENT_PROPOSAL.md` contiene el protocolo.
- **Docker/CI remoto:** los archivos están preparados, pero la plataforma disponible no permitió observar esas ejecuciones.
- **Autenticación ficticia:** se evitó porque un header o usuario simulado no proporciona aislamiento real.
- **Licencia:** pendiente de decisión del titular; no se eligió automáticamente.

## 9. Riesgos pendientes

| Severidad | Riesgo | Impacto | Acción recomendada |
|---|---|---|---|
| Crítica si se publica | Sin autenticación, autorización, tenants, TLS gestionado ni retención | Exposición o mezcla de datos | Mantener loopback/datos sintéticos; diseñar identidad y ciclo de vida antes de cualquier piloto |
| Alta | SQLite solo permite una escritura efectiva y el MVP soporta un worker | 503 o baja capacidad con carga sostenida | Medir WAL/recuperación; migrar a PostgreSQL si hay multiworker o uso compartido |
| Alta | Idempotencia global sería un oráculo de existencia | Filtración entre usuarios futuros | Implementar solo después de tenant, autorización y política de retención |
| Media | El límite ASGI no sustituye límites del servidor/proxy | Un componente anterior puede bufferizar chunks | Repetir límites coherentes en infraestructura antes de desplegar |
| Media | Límite de campo CSV implícito y gramática monetaria amplia | Errores poco específicos o valores no alineados al negocio | T-108: definir longitud, precisión, escala y notación |
| Media | Identificadores compuestos solo por caracteres invisibles | Calidad de datos ambigua | Definir una política explícita y regresiones antes de normalizar/rechazar |
| Media | Advertencia TestClient/HTTPX y rangos amplios en Python 3.11 | Futuras incompatibilidades | T-109: probar migración y ejecutar matriz CI remota |
| Baja | Dashboard sin navegador E2E ni auditoría formal de accesibilidad | Regresiones visuales/de teclado no detectadas | Añadir Playwright y revisión WCAG local cuando esté disponible |
| Baja | Dockerfile no construido en este equipo | Error de empaquetado posible | Construir y hacer smoke test en loopback cuando Docker esté disponible |

## 10. Cómo ejecutar y verificar en Windows

Instalación limpia:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m pytest -q -p no:cacheprovider
uvicorn datatrust_api.main:app --host 127.0.0.1 --port 8000 --workers 1
```

Con el entorno ya existente:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m uvicorn datatrust_api.main:app --host 127.0.0.1 --port 8000 --workers 1
```

Después se puede abrir `http://127.0.0.1:8000/` y cargar `examples/orders_with_issues.csv`, que contiene únicamente datos sintéticos.

## 11. Qué aprendió el desarrollador

- **HTTP y API:** el tamaño del archivo no es el del request multipart. Las cabeceras ayudan, pero una defensa real debe contar los bytes que llegan por ASGI y usar códigos coherentes como 413, 415, 422, 503 y 404.
- **CSV:** es un formato con encoding, comillas, saltos, delimitadores y límites propios. Para exportar hacia hojas de cálculo también hay que tratar una celda como posible fórmula sin destruir la entrada original.
- **SQLite:** `with db` controla commit/rollback, pero no cierra por sí solo la conexión. Una conexión por operación simplifica el MVP; locks, timeout y número de workers deben formar parte del contrato.
- **Pruebas:** primero se demuestra el defecto con una regresión pequeña; después se aplica el cambio mínimo y se ejecutan tanto las pruebas focalizadas como la suite completa. Los límites exactos y la concurrencia coordinada revelan fallos que un caso feliz no muestra.
- **Privacidad:** no almacenar es un control importante. Sustituir nombres por UUID y guardar solo incidencias estáticas reduce exposición, aunque no convierte el sistema en seguro para producción.
- **Arquitectura:** separar HTTP, validación y persistencia permite probar reglas sin servidor, cambiar perfiles sin SQL dinámico y mantener endpoints comprensibles.
- **IA experimental:** un modelo no es una mejora por existir. Requiere pregunta evaluable, datos permitidos, etiquetas, baseline, prevención de leakage y métricas reales; por eso aquí se documentó y no se simuló.

## 12. Próximo hito recomendado

El siguiente hito debería ser **v0.2.1 — confiabilidad publicable local**, dentro de este mismo repositorio:

1. T-109: resolver la transición TestClient/HTTPX y observar la matriz 3.11/3.12 en CI real cuando el titular decida publicar.
2. T-108: definir límites de campo, filas vacías, identificadores invisibles y precisión/escala monetaria, con pruebas antes del código.
3. T-107: experimentar WAL, backup/recuperación y carga multioperación en una copia sintética; conservar un worker hasta tener evidencia.
4. Añadir navegador E2E y evaluación básica de accesibilidad.
5. Diseñar identidad, tenants, autorización y retención antes de T-103 o de cualquier piloto con terceros.

Instrucción exacta de reanudación:

> Lee `AGENTS.md`, `docs/CODEX_PLAN_MAESTRO.md`, `docs/CODEX_PROGRESS.md` y `docs/INFORME_FINAL_CODEX.md`; ejecuta `git status --short --ignored` y `.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider`. Si continúan 74 pruebas verdes, inicia v0.2.1 por T-109 sin repetir v0.1.x/v0.2.0, sin configurar remotos y sin borrar el árbol sin seguimiento.
