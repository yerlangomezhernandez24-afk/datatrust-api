# Informe DataTrust API v0.2.1 — continuación supervisable

Fecha: 27 de octubre de 2026.

## Resumen ejecutivo para reclutadores

DataTrust API aborda un problema común de integración: detectar pedidos CSV incompletos, inconsistentes o peligrosos antes de importarlos. El usuario hipotético es un analista de operaciones o desarrollador que necesita reglas comprensibles por fila/campo. El beneficio sigue siendo una hipótesis —reducir revisión manual y errores de importación—; no existen clientes, ROI ni validación empresarial.

La demo local ofrece API FastAPI/OpenAPI, dos perfiles versionados, validación exacta de importes y campos, SQLite con incidencias minimizadas, exportación protegida y dashboard conectado. v0.2.1 añade política de datos, backup/restauración, experimento WAL, smoke HTTP real, navegador E2E y accesibilidad básica.

Reproducción breve en el entorno existente:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m uvicorn datatrust_api.main:app `
  --host 127.0.0.1 --port 8000 --workers 1
```

Abrir `http://127.0.0.1:8000/` y cargar `examples/orders_with_issues.csv`. Ver `DEMO_3_MINUTOS.md`.

## Estado por fase

| Fase | Estado | Resultado |
|---|---|---|
| 0. Preservación/línea base | COMPLETADA | Backup fuente verificado; baseline 74; entorno, warning y metadata diagnosticados. |
| 1. Calidad de entrada/finanzas | COMPLETADA | Límites, Unicode e importes Decimal explícitos; regresiones y privacidad. |
| 2. SQLite/recuperación | COMPLETADA | Backup/restore/integridad, pruebas y experimento DELETE/WAL; WAL no adoptado. |
| 3. Dashboard/E2E | COMPLETADA | Smoke Uvicorn real, navegador E2E, error accesible y responsive corregido. |
| 4. CI/reproducibilidad | PARCIAL | Checks locales y CI preparada; 3.11, metadata regenerada, CI remoto y Docker bloqueados/no disponibles. |
| 5. IA verificable | COMPLETADA COMO DECISIÓN | No implementada: sin dependencia/dataset/medición que justifique ML. |
| 6. Entrega | COMPLETADA | Documentación v0.2.1, suite final, evidencia, riesgos y continuidad. |

## Preservación y Git

- Rama `main`, sin commits/HEAD, remotos ni identidad Git local/global.
- No se creó commit ni se inventó autor.
- Respaldo previo: `.local-backups/datatrust-v0.2.0-before-v0.2.1-20261027.zip`.
- SHA-256: `0AE498F6631E41F935031549432D67C4CC5E19210C199B421E096D7A05164A5A`.
- `tar -tf` confirmó ausencia de `.git`, `.venv`, backups, bases, cachés, logs, secretos, certificados y metadata generada.
- `.local-backups/` está ignorado por Git y Docker y fuera del package data.

## Cambios implementados

### Política de datos

- Headers: NFC estructural, máximo 64 caracteres/256 bytes y rechazo de Unicode `Cc`/`Cf`.
- Campos conocidos: límites declarados por perfil; extras: 4.096 caracteres/16.384 bytes con incidencia neutral `_extra`.
- Identificadores: controles/formato producen `INVALID_IDENTIFIER`; unicidad usa NFC + `casefold`.
- Importes: `Decimal`, texto decimal sin signo/exponente/coma, rango inclusivo 0.01–999999999999.99 y dos decimales para CRC/USD/EUR; nunca se redondea.
- El parser admite hasta el máximo físico de 2 MiB para que la política semántica, no el techo implícito de 131.072, produzca el error.

### SQLite

- API/CLI de check, backup y restore mediante `Connection.backup()`.
- Origen existente/solo lectura, destino creado en exclusiva, nunca sobrescrito.
- `integrity_check` y `foreign_key_check`; restauración siempre a otra base.
- Experimento coordinado: WAL permitió 20/20 commits con lector activo; DELETE produjo 20/20 BUSY. Se conservó DELETE/un worker por falta de evidencia de recuperación/checkpoint/despliegue.

### Dashboard y E2E

- Ayuda asociada al archivo, scopes de tabla, `aria-busy`, alertas assertive y selección `aria-pressed`.
- Sin `innerHTML`, local/session storage ni CDN; datos dinámicos mediante `textContent`.
- Corrección de min-content que hacía desbordar el dashboard a 390 px.
- Smoke HTTP inicia/detiene Uvicorn loopback y elimina su base temporal.
- Navegador real verificó carga, error, descarga, foco y breakpoint móvil.

### Reproducibilidad

- Fuente 0.2.1 centralizada en `__version__`; check de `pyproject`, paquete, FastAPI y metadata instalada.
- CI 3.11/3.12 preparada con compileall, versión instalada, pip check y pytest.
- Constraints 3.12 revalidados; HTTPX limitado al rango de fallback de Starlette.

## Archivos creados o modificados y justificación

### Raíz/configuración

- `.gitignore`, `.dockerignore`: excluir respaldo local.
- `pyproject.toml`: versión 0.2.1 y rango HTTPX compatible.
- `.github/workflows/tests.yml`: scripts, versión y dependencias en CI.
- `constraints/verified-py312.txt`: fecha de revalidación.
- `README.md`, `README.en.md`, `SECURITY.md`, `CHANGELOG.md`: contrato y evidencia actuales.

### Código

- `__init__.py`, `main.py`: versión única 0.2.1.
- `profiles.py` y ambos JSON: límites, identificadores y políticas decimales estrictas.
- `validator.py`: aplicación de límites/Unicode/importes y parser explícito.
- `db_maintenance.py`: copia/restauración/integridad segura.
- `static/index.html`, `app.js`, `styles.css`: accesibilidad, estados y responsive.

### Scripts

- `check_version.py`: coherencia de versión fuente/instalada.
- `sqlite_maintenance.py`: check/backup/restore local.
- `benchmark_sqlite_journal.py`: experimento DELETE/WAL.
- `smoke_http_e2e.py`: flujo HTTP real en loopback.

### Pruebas

- Nuevos: `test_version.py`, `test_data_policy.py`, `test_db_maintenance.py`, `test_journal_experiment.py`, `test_http_smoke.py`.
- Modificados: `test_profiles.py`, `test_t105.py`, `test_dashboard.py` para el contrato v0.2.1.

### Documentación

- Nuevos: `DATA_POLICY.md`, `DEPENDENCIES.md`, `SQLITE_OPERATIONS.md`, `DEMO_3_MINUTOS.md`, `PROGRESO_CODEX.md` y este informe.
- Actualizados: `PRD.md`, `ARCHITECTURE.md`, `BACKLOG.md`, `PROFILES.md`, `VERIFICACION.md`, `ML_EXPERIMENT_PROPOSAL.md`.
- `.local-backups/MANIFEST.txt` y ZIP: ignorados, solo preservación local.

## Comandos ejecutados y resultados

| Comando/acción | Resultado real |
|---|---|
| `git status --short --ignored`, `git remote -v`, `git log` | sin commits/remotos/identidad; árbol sin seguimiento; log sin HEAD |
| `tar ... .local-backups/...zip` + `tar -tf` + SHA-256 | backup válido, sin entradas prohibidas |
| `.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider` (baseline) | 74 passed, 1 warning, 5.62 s |
| `pytest --collect-only` | 74 casos; 53 funciones + 21 variantes parametrizadas |
| Regresiones de política antes del fix | 12 failed, 6 passed, 1 warning |
| Focalizadas de política finales | 77 passed, 1 warning |
| Suite tras política | 97 passed, 1 warning |
| SQLite focalizadas | 13 passed, 1 warning |
| Journal primer intento | código 1; temporal bloqueado por conexiones del script no cerradas |
| `benchmark_sqlite_journal.py --repeats 20` corregido | código 0; DELETE 20 BUSY, WAL 20 commits, integridad ok |
| Smoke CLI check/backup/restore/check | código 0; integridad origen/destino ok, 6 páginas |
| Dashboard + HTTP focalizadas | 3 passed, 1 warning |
| `smoke_http_e2e.py` | código 0; flujo completo y temporal eliminado |
| Navegador E2E local | ejecutado: carga, perfil, historial, tabla, descarga, 415, foco y 390 px |
| `node --check static/app.js` | código 0 |
| `check_version.py` | código 0; fuente/pyproject/FastAPI 0.2.1 |
| `check_version.py --installed` | código 1 esperado; metadata antigua 0.1.1 |
| `compileall` y `pip check` | código 0; sin dependencias rotas |
| Suite posterior al bump | 105 passed, 1 warning, 6.43 s |
| Suite final posterior al cierre documental | 105 passed, 1 warning, 6.34 s |
| Recolección final | 105 tests collected, 0.97 s |

Los checks finales de `compileall`, `pip check`, JavaScript y versión fuente terminaron con código 0. El hash/archivo del backup, exclusiones, archivos residuales y ausencia de remotos fueron revalidados.

## Matriz de ejecución

| Componente | Estado | Evidencia |
|---|---|---|
| Python 3.12.14 | EJECUTADO | suite/checks/smokes locales |
| Python 3.11 | NO EJECUTADO | no instalado; `py` no existe |
| Navegador E2E | EJECUTADO | navegador integrado con superficie Playwright |
| Playwright como paquete | NO INSTALADO | no se añadió; no era necesario para el navegador disponible |
| Docker | NO EJECUTADO | comando no disponible |
| GitHub Actions | NO EJECUTADO | repo no publicado/sin remoto |
| Ruff/Black/mypy/YAML parser | NO EJECUTADO | herramientas no disponibles |
| ML/scikit-learn | NO EJECUTADO | paquete ausente y sin dataset etiquetado |

## Seguridad y por qué no está lista para Internet

Controles locales presentes: límite ASGI real, archivo/filas/campos acotados, SQL parametrizado, transacciones, cierre explícito, nombres neutrales, no persistencia de filas, CSP básica y exportación anti-fórmula.

La aplicación carece de autenticación, autorización, tenants, TLS gestionado, rate limiting distribuido, cifrado en reposo, retención/borrado verificable, auditoría empresarial, pentest, monitoreo y respuesta a incidentes. SQLite/un worker no es arquitectura multiusuario. El límite ASGI tampoco sustituye límites de proxy/servidor. Por ello solo se soportan loopback y datos sintéticos.

La metadata instalada vieja no afecta el código fuente ejecutado, pero sí demuestra que una instalación limpia y CI observada son requisitos antes de distribuir el paquete.

## IA: conclusión con evidencia

`scikit-learn=False` y no existe dataset etiquetado que mida valor incremental frente a la nueva baseline. Implementar un modelo sobre anomalías sintéticas diseñadas para él produciría evidencia circular. Se conserva un protocolo con split, baseline, leakage y métricas, pero la conclusión v0.2.1 es: **ML no aporta valor demostrado todavía**. No hay endpoint, modelo, predicciones ni métricas inventadas.

## Cinco conceptos para explicar en entrevista

### 1. ¿Por qué `Decimal` y no `float` para importes?

Respuesta correcta: `float` representa fracciones binarias y puede introducir errores como 0.1 + 0.2. `Decimal` interpreta texto decimal exactamente. Aun así se necesita una gramática, rango y escala; `Decimal('1e2')` sería válido matemáticamente, pero el contrato puede prohibirlo.

### 2. ¿Por qué `Content-Length` no basta para limitar uploads?

Respuesta correcta: la cabecera puede faltar o ser falsa y no representa necesariamente los chunks reales. El middleware cuenta mensajes ASGI antes del parser; el archivo tiene además su propio límite porque multipart añade overhead. Un proxy futuro también necesitaría un límite coherente.

### 3. ¿Qué diferencia hay entre transacción y cierre SQLite?

Respuesta correcta: `with connection` confirma o revierte, pero no garantiza cerrar el descriptor. `closing(connection)` libera la conexión. Transacciones cortas protegen ejecución + incidencias; timeout/503 maneja contención sin fingir writers paralelos.

### 4. ¿Por qué usar `Connection.backup()` y no copiar el archivo?

Respuesta correcta: SQLite puede estar activo y, con WAL, los sidecars contienen cambios. La API de backup toma un snapshot coherente. La herramienta verifica integridad y restaura a una ruta nueva, evitando sobrescribir la base del usuario.

### 5. ¿Qué demuestra una buena prueba de regresión?

Respuesta correcta: primero reproduce un defecto con una expectativa de contrato, luego pasa tras un cambio mínimo y finalmente se ejecuta toda la suite. Debe controlar límites/concurrencia sin sleeps aleatorios y no borrar una prueba vieja cuando el contrato cambia; se actualiza con justificación.

## Próxima iteración: exactamente tres prioridades

1. **T-109: entorno limpio y compatibilidad de tests.** Aceptación: instalar desde cero en Python 3.11 y 3.12, metadata 0.2.1 coherente, cero warning tras migración validada a `httpx2`, `pip check` y suite verdes; observar GitHub Actions solo cuando el titular publique.
2. **Recuperación/WAL/contenedor.** Aceptación: pruebas de terminación abrupta, checkpoint y backup/restauración en volumen Docker local; build/smoke loopback ejecutados; decisión WAL adoptar/rechazar con evidencia, manteniendo un worker.
3. **Diseño pre-piloto de identidad y ciclo de vida.** Aceptación: threat model, tenant/authorization y retención/borrado especificados y probados antes de T-103; ninguna exposición pública ni datos reales hasta cumplirlos.

## Reanudación exacta

> Lee `AGENTS.md`, `docs/PROGRESO_CODEX.md`, `docs/INFORME_V0_2_1_CODEX.md` y `docs/VERIFICACION.md`. Verifica el hash del backup, ejecuta `git status --short --ignored`, `.\.venv\Scripts\python.exe scripts/check_version.py` y `.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider`. No repitas v0.2.1 ni reemplaces el árbol con el ZIP. Continúa por T-109 solo si hay Python 3.11/3.12 y build tools locales; no configures remotos, no inventes identidad y no publiques.
