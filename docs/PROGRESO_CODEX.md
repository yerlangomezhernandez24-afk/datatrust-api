# Progreso Codex — de v0.2.1 a v1.0.0

Última actualización: 27 de octubre de 2026.

## Estado de fases

| Fase | Estado | Evidencia actual |
|---|---|---|
| 0. Preservación y línea base | COMPLETADA | Respaldo verificado, baseline 74/74, entorno y bloqueo de metadata documentados, check de versión añadido. |
| 1. Calidad de entradas y garantías financieras | COMPLETADA | Política explícita, regresiones rojas, perfiles ampliados y suite completa de 97 casos verde. |
| 2. SQLite, backups y recuperación | COMPLETADA | API backup/restore/integridad, CLI, pruebas y experimento DELETE/WAL ejecutado; WAL no adoptado. |
| 3. Dashboard y E2E | COMPLETADA | Smoke HTTP real, navegador E2E, accesibilidad y responsive verificados; overflow móvil corregido. |
| 4. CI y reproducibilidad | COMPLETADA LOCAL Y CI | Versión/metadata 1.0.0 coherentes; Python 3.11/3.12 aprobados en GitHub Actions. Docker no ejecutado. |
| 5. IA verificable | COMPLETADA COMO DECISIÓN | scikit-learn ausente y sin dataset etiquetado; no se implementó ML ni se inventaron métricas. |
| 6. Entrega y continuidad | COMPLETADA | Informe, verificación final, árbol Git y reanudación cerrados. |
| 7. Cierre integral de calidad | COMPLETADA | Snapshot preservado, 109/109, instalación limpia, E2E responsive e informe v0.3.0. |
| 8. Cierre final de portafolio | COMPLETADA | 113/113, demos 6/100, wheel final, E2E real, materiales de publicación y v1.0.0. |
| 9. Publicación GitHub | COMPLETADA | Repositorio público, autoría preservada, CI verde, topics y auditoría de privacidad verificados. |

## Fase 0 — registro parcial

- Repositorio: rama `main`, sin `HEAD`, commits, remotos ni identidad Git local/global.
- Todos los archivos del proyecto siguen sin seguimiento; no se limpió ni sobrescribió el árbol.
- Respaldo: `.local-backups/datatrust-v0.2.0-before-v0.2.1-20261027.zip`.
- SHA-256: `0AE498F6631E41F935031549432D67C4CC5E19210C199B421E096D7A05164A5A`.
- `tar -tf` verificó que no contiene `.git`, `.venv`, backups, bases, runtime data, cachés, logs, secretos, certificados ni metadata generada.
- `.local-backups/` quedó ignorado por Git y Docker; no forma parte de los paquetes de Python.

## Fase 0 — línea base cerrada

- Suite inicial: `74 passed, 1 warning in 5.62s`.
- Recolección: 74 casos provenientes de 53 funciones de prueba. Siete decoradores `pytest.mark.parametrize` expanden 21 variantes adicionales; esto explica 53 funciones frente a 74 casos actuales. Los hitos 28 y 53 permanecen explicados en `VERIFICACION.md`.
- `python -m compileall -q src tests scripts`: código 0.
- `python -m pip check`: `No broken requirements found.`
- Entorno: Python 3.12.14 de `.venv`, Windows 11, SQLite 3.53.1, FastAPI 0.162.0, Starlette 1.10.0, Pydantic 2.14.1, Uvicorn 0.54.0, python-multipart 0.0.32, pytest 9.1.1 y HTTPX 0.28.1.
- No están disponibles el lanzador `py`, un alias `python` funcional, Python 3.11 ni Docker. Node v24.22.1 sí está disponible.
- SQLite sintético: `threadsafety=3`, `journal_mode=delete`, `synchronous=2` (`FULL`) e `integrity_check=ok`. `foreign_keys` inicia apagado en SQLite puro y la aplicación lo activa por conexión.
- Advertencia exacta: Starlette 1.10.0 intenta importar `httpx2`; al no existir, usa HTTPX 0.28.1 y emite `StarletteDeprecationWarning` desde el puente `fastapi.testclient`. No se ocultó ni se instaló un paquete especulativo.
- Metadata: fuente/`pyproject`/FastAPI coinciden en 0.2.0; `importlib.metadata` lee 0.1.1 desde el `dist-info` editable antiguo. No es un error del `pyproject`, sino metadata generada obsoleta.
- La reinstalación editable permanece bloqueada localmente: la venv no contiene `setuptools` ni `wheel`, `ensurepip` solo incluye pip y no existe una rueda en caché. No se habilitó red ni se modificó Python global.
- `scripts/check_version.py` comprueba fuente/`pyproject`/FastAPI y opcionalmente metadata instalada. El modo fuente terminó 0; `--installed` terminó 1 y reportó exactamente 0.1.1. CI ejecutará el modo instalado después de una instalación limpia.
- Prueba focalizada de consistencia fuente: `1 passed in 0.53s`.

## Archivos modificados hasta ahora

- `.gitignore`: excluye el respaldo local.
- `.dockerignore`: excluye el respaldo del contexto Docker.
- `.local-backups/MANIFEST.txt`: registra alcance y hash; también está ignorado.
- `docs/PROGRESO_CODEX.md`: este registro persistente.
- `scripts/check_version.py` y `tests/test_version.py`: comprobación reproducible de versión.
- `.github/workflows/tests.yml`: valida también la metadata instalada en entornos CI limpios.

## Fase 1 — COMPLETADA

- Política previa al código: `docs/DATA_POLICY.md` define UTF-8/BOM, encabezados, longitudes en caracteres/bytes, Unicode, filas vacías, columnas extra, privacidad e importes.
- Ciclo rojo: `tests/test_data_policy.py` produjo `12 failed, 6 passed, 1 warning in 1.66s` sobre el código v0.2.0.
- Defectos reproducidos: signos `+`, exponente, escala >2, rango excesivo y formatos incompletos aceptados; ausencia de límites; identificadores con NUL/zero-width aceptados; header sin política; campo de 140.000 caracteres interceptado por el límite implícito del parser.
- Perfiles locales ahora declaran `identifier_fields`, `field_limits` y `decimal_policies`, validados con claves/tipos/referencias estrictas.
- Importes: `Decimal`, gramática ASCII sin signo/exponente/coma, rango 0.01–999999999999.99 y escala máxima de dos por CRC/USD/EUR. No hay redondeo silencioso.
- Valores conocidos aplican límites por perfil; columnas extra usan un límite general y una incidencia neutral `_extra` para no persistir nombres arbitrarios.
- Encabezados se recortan y normalizan a NFC para estructura; controles/formato o exceso producen 422 sin eco del nombre.
- Identificadores con `Cc`/`Cf` producen `INVALID_IDENTIFIER`. La unicidad conserva NFC + `casefold`.
- El techo del parser CSV se elevó al máximo físico del archivo para que un campo grande llegue a la política explícita.
- Contrato histórico actualizado con justificación: dos importes finitos de ~1.000 caracteres que T-105 aceptaba ahora deben producir `VALUE_TOO_LONG`.
- Pruebas focalizadas finales: `77 passed, 1 warning in 3.17s`.
- Suite completa: `97 passed, 1 warning in 4.95s`.

Archivos de la fase: `docs/DATA_POLICY.md`, `docs/PROFILES.md`, ambos perfiles JSON, `profiles.py`, `validator.py`, `tests/test_data_policy.py`, `tests/test_profiles.py` y `tests/test_t105.py`.

## Fase 2 — COMPLETADA

- Ciclo rojo inicial: dos errores de colección porque `db_maintenance` y el experimento todavía no existían.
- `db_maintenance.py` verifica bases existentes en modo solo lectura, usa `Connection.backup()`, crea destinos en forma exclusiva, valida el resultado y nunca sobrescribe una ruta existente.
- Restauración únicamente hacia una base distinta/nueva; origen ausente, origen=destino y corrupción tienen errores explícitos. Un destino parcial creado por la propia operación se elimina si la copia falla.
- Pruebas: round trip con incidencias, snapshot anterior a cambios posteriores, no sobrescritura, fuente ausente, misma ruta, corrupción sin eco y backup con lector abierto.
- Pruebas SQLite focalizadas finales: `13 passed, 1 warning in 1.81s`.
- Primer experimento falló al limpiar temporales en Windows: dos conexiones del script seguían abiertas porque el context manager de `sqlite3.Connection` controla transacción pero no cierre. Se corrigió con `closing`; la regresión focalizada pasó (`1 passed in 0.17s`).
- Experimento final, 20 repeticiones, lector activo y timeout cero: DELETE produjo 20/20 `BUSY` (mediana 0,495750 ms); WAL confirmó 20/20 (mediana 10,856050 ms); todas las integridades `ok`, SQLite 3.53.1 y `synchronous=FULL`.
- La latencia no se compara como throughput porque DELETE falla rápido y WAL confirma; la evidencia es solo de convivencia lector/writer.
- Decisión: conservar DELETE/un worker. WAL no se impone sin probar checkpoints, cierres abruptos, Docker, filesystem y volumen persistente.
- Smoke real del CLI: `check`, `backup`, `restore`, `check` terminaron 0; ambos reportes tuvieron integridad origen/destino `ok` y 6 páginas.
- Suite completa: `103 passed, 1 warning in 5.06s`.

Archivos de la fase: `src/datatrust_api/db_maintenance.py`, `scripts/sqlite_maintenance.py`, `scripts/benchmark_sqlite_journal.py`, `tests/test_db_maintenance.py`, `tests/test_journal_experiment.py` y `docs/SQLITE_OPERATIONS.md`.

## Fase 3 — COMPLETADA

- Playwright no existe como paquete/comando local, pero la herramienta de navegador instalada expuso automatización Playwright sobre el navegador integrado; no se instaló nada.
- HTML: ayuda vinculada al input de archivo, encabezados con `scope=col` y estados/paginación anunciados.
- JavaScript: errores cambian el estado a `role=alert`/`aria-live=assertive`, formulario marca `aria-busy`, ejecución seleccionada usa `aria-pressed`; los datos continúan con `textContent`, sin `innerHTML` ni storage del navegador.
- Smoke HTTP real autónomo: todos los estados esperados (`health/dashboard/profiles/list/detail/pages/export=200`, carga=201, desconocido=404), perfil USD, BOM presente y base temporal eliminada.
- Pruebas focalizadas dashboard/smoke: `3 passed, 1 warning in 2.30s`.
- Navegador real: perfil USD seleccionado; carga de `orders_with_issues.csv`; métricas visibles 6 totales/0 válidas/6 inválidas/9 incidencias; historial, tabla y descarga comprobados.
- Error real: subir el JSON sintético produjo 415 y texto `Se aceptan únicamente archivos .csv`; DOM confirmó `role=alert` y `aria-live=assertive`.
- Teclado: botón enfocado mostró outline sólido de 2,4 px. No se ejecutó una auditoría WCAG formal.
- Responsive: a 390×844 se detectó overflow (`scrollWidth > 390`, track de workspace ~596 px). Se corrigió `min-width:0` y wrapping; repetición: `scrollWidth=375`, workspace 359,2 px y `bodyFitsViewport=true`. Viewport restaurado a 1280.
- Servidor limitado a `127.0.0.1:8765`, un worker y base temporal. Al terminar: pestaña cerrada, proceso detenido, DB eliminada y ningún listener en 8765.
- `node --check src/datatrust_api/static/app.js`: código 0.
- Suite completa: `104 passed, 1 warning in 6.64s`.

Archivos de la fase: `static/index.html`, `static/app.js`, `static/styles.css`, `tests/test_dashboard.py`, `tests/test_http_smoke.py`, `scripts/smoke_http_e2e.py` y `docs/DEMO_3_MINUTOS.md`.

## Fase 4 — COMPLETADA LOCAL / PARCIAL EXTERNA

- Versión fuente elevada a 0.2.1 en `pyproject.toml` y paquete; FastAPI y `/health` importan `__version__` para evitar duplicación.
- Check fuente: `pyproject=package=fastapi=0.2.1`, código 0. Check `--installed`: código 1, porque la metadata editable vieja sigue en 0.1.1.
- Bloqueo de metadata: sin `setuptools`, `wheel`, módulo `build` ni ruedas cacheadas; no se descargaron paquetes ni se modificó Python global.
- Dependencia de HTTPX acotada a `<0.29`, coherente con el fallback declarado por Starlette 1.10.0. `httpx2>=2` aparece solo en su extra `full`, no está instalado y no se añadió sin verificación.
- CI compila `src/tests/scripts`, comprueba versión instalada, `pip check` y pytest para 3.11/3.12. GitHub Actions remoto NO EJECUTADO.
- Entorno local: solo Python 3.12.14 dentro de `.venv`; Python 3.11 NO EJECUTADO. `py` ausente y el alias `python` apunta al stub de Microsoft Store.
- Ruff, Black, mypy, PyYAML, Playwright de paquete, build, setuptools y wheel no están disponibles. No se instalaron dependencias solo para decorar CI. YAML se revisó manualmente, no mediante parser.
- Docker continúa ausente y NO EJECUTADO.
- `compileall`, `pip check` y `node --check`: código 0; `pip check` sin dependencias rotas.
- Suite completa tras el bump: `105 passed, 1 warning in 6.43s`.

Archivos de la fase: `pyproject.toml`, `__init__.py`, `main.py`, workflow CI, constraints, `docs/DEPENDENCIES.md`, README ES/EN, PRD, arquitectura, backlog, changelog y SECURITY.

## Fase 5 — COMPLETADA COMO DECISIÓN DE NO IMPLEMENTAR

- `scikit-learn=False` revalidado; no existe Playwright de paquete ni herramientas ML instaladas.
- No existe dataset etiquetado que permita comparar honestamente un detector contra la nueva baseline T-108.
- `ML_EXPERIMENT_PROPOSAL.md` conserva pregunta, split, prevención de leakage, métricas y límites, y añade la conclusión `no aporta valor aún`.
- No se creó endpoint, modelo, dataset engañoso ni porcentaje de mejora inventado.

## Fase 6 — COMPLETADA

- `docs/INFORME_V0_2_1_CODEX.md` contiene resumen para reclutadores, fases, archivos, comandos, matriz ejecutado/no ejecutado, seguridad, IA, cinco preguntas didácticas y tres prioridades.
- Suite final: `105 passed, 1 warning in 6.34s`.
- Recolección final: `105 tests collected in 0.97s`.
- `compileall`, `pip check`, `node --check` y versión fuente: código 0.
- Hash de respaldo revalidado sin cambios; archivo ignorado y sin entradas prohibidas.
- Revisión del árbol: no se encontraron `.env`, bases, claves o certificados fuera de entornos/backups ignorados.
- Git final: rama `main`, sin HEAD/commits, identidad o remotos; todo el proyecto continúa sin seguimiento por la inicialización tardía. No se limpió ni publicó.
- `.pytest_cache` continúa generando una advertencia de permisos al listar ignorados, pero se ejecutó pytest con `-p no:cacheprovider` y no afectó pruebas.

## Siguiente acción exacta

Lee `AGENTS.md`, este archivo, `INFORME_V0_2_1_CODEX.md` y `VERIFICACION.md`; verifica hash/Git y ejecuta versión fuente + suite. Continúa únicamente con una de las tres prioridades del informe, comenzando por T-109 si existen intérpretes/build tools locales. No repitas v0.2.1, no reemplaces el árbol con el ZIP, no configures remotos ni publiques.

## Fase 7 — cierre integral de calidad COMPLETADA

- Se leyó el nuevo prompt de cierre y se revalidaron instrucciones, documentos,
  fuente, pruebas, dashboard, Dockerfile y workflow real `tests.yml`.
- Línea base del 27 de octubre de 2026: `105 tests collected in 0.69s` y
  `105 passed, 1 warning in 6.60s`.
- `pip check`, `compileall`, `node --check` y smoke HTTP real terminaron con
  código 0. El smoke usó `127.0.0.1`, un worker y eliminó la DB temporal.
- Fuente/API/pyproject son 0.2.1; metadata editable sigue en 0.1.1. La venv
  inicial no contiene `setuptools`, `wheel` ni `httpx2`.
- Inventario medido: 68 archivos, 262.516 bytes y 4.502 líneas fuera de
  entornos/backups. Se conserva la arquitectura; no se justifica reescritura.
- Snapshot nuevo: `.local-backups/datatrust-v0.2.1-before-quality-close-20261027.zip`,
  SHA-256 `B7830A34CF7700A9AE09BE8C09022D1F70EE57FDF3B80C4C159123BB0C8DD6C3`,
  89 entradas y cero entradas prohibidas.
- `docs/PLAN_CIERRE_CALIDAD.md` contiene prioridades, aceptación y evidencia.
- Instalación limpia `.venv-verify-py312`: paquete/metadata/FastAPI/pyproject
  0.3.0, `pip check` correcto, 109 pruebas sin warnings y smoke real verde.
- `httpx2 2.16.0` reemplazó el fallback HTTPX; constraints ampliado con las
  transitivas realmente observadas. Python 3.11 continúa NO EJECUTADO.
- Regresiones backend reprodujeron cuatro defectos: headers ausentes, fórmula
  tras controles, eco de perfil y lock de lectura como 500. Todos quedaron
  corregidos con 503/mensajes estáticos/protección y suite focalizada verde.
- Dashboard rediseñado sin dependencias externas; navegador real validó carga,
  422, exportación, teclado, consola y 360/390/768/1366 sin overflow.
- Smoke final añadió 413/sin persistencia y headers; benchmark se repitió dos
  veces. Docker y CI remota siguen NO EJECUTADOS por ausencia de herramienta/
  remoto. ML sigue NO EJECUTADO por falta de dataset etiquetado defendible.
- Wheel 0.3.0 construido e inspeccionado con assets; `build/` y todas las venvs
  de verificación están ignorados. No se creó commit, remoto ni publicación.
- Documentos de cierre: `DEMO_RECLUTADOR.md`, `PLAN_CIERRE_CALIDAD.md`,
  `INFORME_CIERRE_CALIDAD_CODEX.md`, README ES/EN y evidencia actualizada.

## Fase 8 — cierre final de portafolio COMPLETADA

- Se leyó el prompt final, `AGENTS.md`, documentación vigente/histórica,
  fuente, pruebas, scripts, assets, empaquetado, workflow y Dockerfile.
- Línea base independiente: Python 3.12.14, 109 pruebas descubiertas y 109
  aprobadas sin warnings en 7,03 s; smoke HTTP real verde.
- Snapshot previo: `.local-backups/datatrust-v0.3.0-before-v1-close-20261027.zip`,
  SHA-256 `6A25037EF134CD38C9A90FB92EB96031296D1928029571D3DDAF5BD83C6FF730`,
  77 entradas y cero prohibidas.
- Las nuevas regresiones fallaron primero por faltar `demo-orders-6.csv`,
  `demo-orders-100.csv` y sus enlaces. Tras incorporar recursos: 5 pruebas
  focalizadas verdes; suite ampliada a 113.
- Demos reales: 6/2/4/5 y 100/90/10/10 (total/válidas/inválidas/incidencias).
- Venv limpia desde fuente: 113 pruebas aprobadas sin warnings en 7,13 s,
  `compileall`, `node --check`, `pip check` y versión 1.0.0 correctos.
- Wheel final: 32.718 bytes, SHA-256
  `D445445C631713F17B0C80A2994B26801E45CDC7151192C426743618D1DA2A3E`;
  instalado en otra venv, recursos y demos comprobados desde `site-packages`.
- Smoke desde wheel: health/dashboard/perfiles/list/detalle/páginas/export=200,
  carga=201, desconocido=404, sobredimensionado=413 sin persistencia, BOM y
  headers defensivos correctos.
- Navegador real: 360×800, 390×844, 768×1024 y 1366×768 sin overflow de página;
  demos 6/100, selección USD, 422 anunciado, descarga y foco/skip-link.
- Git permanece local, sin commits, remoto o identidad. No se añadió licencia,
  no se publicó nada y los campos de autor quedan explícitamente pendientes.
- Decisión: GO v1.0.0 como **Portfolio Local Release — Not Production Ready**.
  Alcance general congelado; solo defectos bloqueantes concretos deben reabrirlo.

## Fase 9 — publicación GitHub COMPLETADA

- Repositorio público:
  `https://github.com/yerlangomezhernandez24-afk/datatrust-api`.
- Commit de referencia v1.0.0:
  `84b7b1b3c59160a5cb870f402766498fa20bf7ec`.
- Actualización de Actions:
  `cffa751028bc625f29f4cc80c2575116ff97afda`.
- GitHub Actions aprobó Python 3.11 y 3.12 en 27 s:
  `https://github.com/yerlangomezhernandez24-afk/datatrust-api/actions/runs/40632875253`.
- La primera ejecución fue verde, pero mostró advertencias de runtimes Node
  obsoletos; se actualizaron `checkout` y `setup-python` a v7 y la segunda
  ejecución quedó sin esas advertencias.
- No se publicaron bases, respaldos, entornos virtuales, secretos, caches,
  artefactos de build ni datos reales. No se desplegó la aplicación.
- Sigue pendiente una decisión del titular sobre `LICENSE`; Docker tampoco se
  ejecutó.
