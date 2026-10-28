# Progreso persistente de Codex

Última actualización: 26 de octubre de 2026.

## Estado verdadero al recibir el prompt maestro

- Repositorio real: `<RUTA_LOCAL>\DataTrust_API_Starter`.
- Git fue inicializado localmente en `main`; no tiene commits, `HEAD` ni remotos.
- No existe identidad Git local o global (`user.name`/`user.email`), por lo que no se creó un commit ni se inventó autor.
- Todos los archivos del proyecto están sin seguimiento porque el repositorio acaba de inicializarse. `.venv`, `egg-info`, cachés, bases SQLite y sidecars, cobertura, logs y secretos están ignorados.
- Fuente declarada: v0.2.0. Metadato de la instalación editable: 0.1.1; el intento local sin red de refrescarlo falló porque el entorno no contiene `setuptools.build_meta`. No se descargó nada.
- Entorno observado: Windows, Python 3.12.14, SQLite 3.53.1, FastAPI 0.162.0, Starlette 1.10.0, Pydantic 2.14.1, Uvicorn 0.54.0, python-multipart 0.0.32, pytest 9.1.1 y HTTPX 0.28.1.

## Trabajo ya presente y verificado

- v0.1.1: sufijo real `.csv`, nombre técnico neutral, offset acotado, cierre/rollback SQLite, rechazo `:memory:` y trabajo bloqueante fuera del event loop.
- v0.1.2/T-105: límites exactos de bytes/filas, multipart vs archivo, Unicode/encoding, esquemas, fechas/importes, paginación real, privacidad/fórmulas y concurrencia SQLite.
- Defectos corregidos: duplicados NFC/NFD, controles/formato en email y `SQLITE_BUSY/LOCKED` traducido a HTTP 503 sin persistencia parcial.
- Último resultado completo antes de crear este registro: 53 pruebas aprobadas, una advertencia TestClient/HTTPX. Debe repetirse porque se reforzó después una aserción de esquema.

## Registro de fases

### Fase 0 / A — COMPLETADA

- Documentos requeridos, código, Docker y CI inspeccionados.
- `docs/CODEX_PLAN_MAESTRO.md` y este registro creados.
- Línea base repetida sobre el último contenido: `53 passed, 1 warning in 3.66s`.

### Fase B — COMPLETADA (v0.1.3)

- Pruebas rojas iniciales: importación ausente del middleware; luego 3 fallos porque Starlette convertía la señal del `receive` en 400.
- Implementado conteo de bytes ASGI previo al multipart, supresión del 400 interno y respuesta 413 estable.
- Focalizadas HTTP/SQLite: `11 passed, 1 warning in 1.36s`.
- Suite completa: `60 passed, 1 warning in 3.38s`.
- Dockerfile usa usuario no root, directorio de datos escribible y `--workers 1`. `docker` no existe en este host; build/run NO EJECUTADOS.
- WAL no se activó: queda pendiente T-107 para no cambiar persistentemente bases existentes sin política de filesystem/recuperación.

### Fase C1/C2 — COMPLETADA (v0.2.0)

- T-102: 105 incidencias exportadas frente a 100 del detalle; streaming `fetchmany(500)`, UTF-8 BOM, nombre neutro y protección de fórmula tras whitespace.
- T-101: registro local de dos perfiles, JSON con claves/tipos/referencias estrictos, rechazo de claves duplicadas/rutas desconocidas y endpoint de catálogo.
- Focalizadas: exportación `3 passed`; perfiles + API/validator `34 passed`.

### Fase C3 — BLOQUEADA POR DISEÑO

- No se implementó idempotencia global: sin tenant/autorización podría funcionar como oráculo de existencia de archivos.
- Política, esquema futuro y pruebas requeridas en `IDEMPOTENCY_DESIGN.md`.

### Fase D — COMPLETADA

- Dashboard HTML/CSS/JS empaquetado y servido en `/`, sin CDN.
- Carga, perfiles, métricas, historial, selección, paginación y descarga conectados.
- Integración backend del flujo y assets: `2 passed`; `node --check` código 0.

### Fase E — NO EJECUTADA

- `scikit-learn=False` en el entorno. Se conservó P2 como protocolo científico en `ML_EXPERIMENT_PROPOSAL.md`; no hay modelo ni métricas simuladas.

### Fase F — COMPLETADA

- Matriz CI 3.11/3.12 configurada; ejecución remota pendiente.
- Constraints exactos del entorno 3.12, `pip check` verde y `compileall` verde.
- Benchmark T-104 ejecutado y documentado.
- Dockerfile no root/un worker, pero `docker` no está instalado: build/run no ejecutados.
- Suite completa intermedia v0.2.0: `74 passed, 1 warning in 4.55s`.
- Suite completa final: `74 passed, 1 warning in 4.23s`.
- `compileall`, `pip check` y `node --check` terminaron con código 0; `pip check` informó `No broken requirements found.`
- Revisión Git final: rama `main`, sin `HEAD`, commits, remotos ni identidad; todos los archivos del proyecto permanecen sin seguimiento y los artefactos generados están ignorados.
- Informe de cierre creado en `docs/INFORME_FINAL_CODEX.md`.

## Reanudación literal

> Lee `AGENTS.md`, `docs/CODEX_PLAN_MAESTRO.md`, `docs/CODEX_PROGRESS.md` y `docs/INFORME_FINAL_CODEX.md`; ejecuta `git status --short --ignored` y `.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider`. Si continúan 74 pruebas verdes, inicia v0.2.1 por T-109 sin repetir v0.1.x/v0.2.0, sin configurar remotos y sin borrar el árbol sin seguimiento.
