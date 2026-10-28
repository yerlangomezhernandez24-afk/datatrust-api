# Informe de cierre — DataTrust API v1.0.0

Fecha: 27 de octubre de 2026
Clasificación: **Portfolio Local Release — Not Production Ready**

## 1. Decisión

**GO para v1.0.0 como demo local de portafolio.**

Los recorridos P0 funcionan, la suite completa está verde, la instalación desde
fuente y wheel es reproducible en el entorno disponible, los recursos están
empacados y el navegador real completó casos nominales y de error. GO no
significa aprobación para producción: faltan controles esenciales y nunca se
probó exposición pública.

## 2. Versión, fecha y Git

- `pyproject.toml`, paquete, OpenAPI/FastAPI, `/health` y metadata instalada:
  `1.0.0`.
- Python 3.12.14; pip 25.0.1; SQLite 3.53.1; Windows 11 build 26200.
- Git local en rama `main`, sin `HEAD`/commits, remoto o identidad de autor.
- Todos los archivos del proyecto continúan sin seguimiento debido a la
  inicialización tardía de Git. No se ejecutó `git add`, commit, push ni creación
  de remoto. Nada fue publicado.
- Respaldo previo preservado en
  `.local-backups/datatrust-v0.3.0-before-v1-close-20261027.zip`, SHA-256
  `6A25037EF134CD38C9A90FB92EB96031296D1928029571D3DDAF5BD83C6FF730`.

## 3. Archivos

### Creados

- `src/datatrust_api/static/demo-orders-6.csv`
- `src/datatrust_api/static/demo-orders-100.csv`
- `tests/test_portfolio_release.py`
- `scripts/iniciar_demo.ps1`
- `docs/PLAN_RELEASE_V1.md`
- `docs/DATOS_PENDIENTES_PUBLICACION.md`
- `docs/GUIA_DEMO_USUARIO.md`
- `docs/CASO_DE_ESTUDIO_PORTAFOLIO.md`
- `docs/EXTRACTO_CV_LINKEDIN.md`
- `docs/CHECKLIST_PUBLICACION_GITHUB.md`
- este informe

### Editados

- Versión/paquete: `pyproject.toml`, `src/datatrust_api/__init__.py`.
- UI/pruebas: `static/index.html`, `static/styles.css`,
  `tests/test_dashboard.py`.
- Presentación: `README.md`, `README.en.md`, `CHANGELOG.md`, `AGENTS.md`,
  `SECURITY.md`, `docs/DEMO_RECLUTADOR.md`.
- Especificación/evidencia: `PRD.md`, `ARCHITECTURE.md`, `BACKLOG.md`,
  `VERIFICACION.md`, `PROGRESO_CODEX.md`, `BENCHMARK.md`, `DEPENDENCIES.md`,
  `DATA_POLICY.md`, `PROFILES.md`, `SQLITE_OPERATIONS.md`.
- Se reemplazaron dos rutas locales privadas por `<RUTA_LOCAL>` en
  `CODEX_PROGRESS.md` e `INFORME_CIERRE_CALIDAD_CODEX.md`.

### Inspeccionados y no modificados funcionalmente

`main.py`, `validator.py`, `store.py`, `profiles.py`, `csv_export.py`,
`db_maintenance.py`, modelos, perfiles JSON, Dockerfile y workflow CI. El
backend v0.3.0 ya satisfacía el contrato; no se justificó un refactor. No se
tocaron bases o backups previos del usuario.

## 4. Comandos y resultados reales

| Verificación | Resultado |
|---|---|
| Baseline `pytest --collect-only` | 109 casos en 1,48 s |
| Baseline `pytest -q` | 109 passed, 0 warnings, 7,03 s |
| Regresión inicial de demos | 3 failed: recursos/enlaces ausentes |
| Focalizadas tras implementación | 5 passed en 1,12 s |
| Recolección final en venv limpia | 113 casos en 0,58 s |
| Suite limpia desde fuente | 113 passed, 0 warnings, 7,13 s |
| Suite final tras UI/docs | 113 passed, 0 warnings, 7,22 s |
| `compileall` / `node --check` | códigos 0 |
| `pip check` | No broken requirements found |
| `check_version.py --installed` | cuatro fuentes = 1.0.0 |
| Smoke Uvicorn desde wheel | 200/201/404/413 esperados, sin persistencia parcial |
| Backup/restauración/concurrencia | cubiertos por suite; bases sintéticas temporales |

Instalación limpia desde fuente:

```powershell
python -m venv .venv-v1-source-py312
.\.venv-v1-source-py312\Scripts\python.exe -m pip install -c constraints\verified-py312.txt -e ".[dev]"
```

Wheel final:

- archivo: `datatrust_api-1.0.0-py3-none-any.whl`;
- tamaño: 32.718 bytes;
- SHA-256: `D445445C631713F17B0C80A2994B26801E45CDC7151192C426743618D1DA2A3E`;
- instalado en una segunda venv; el módulo se cargó desde `site-packages`;
- recursos presentes: HTML, CSS, JS, favicon SVG, perfiles JSON y demos 6/100.

El smoke desde wheel verificó health, dashboard, perfiles, historial, detalle,
páginas y exportación en 200; carga en 201; desconocido 404; sobredimensionado
413 sin persistencia; BOM y cabeceras defensivas; base temporal eliminada.

Rendimiento del validador puro (cinco repeticiones): medianas de 1,697 ms,
16,832 ms y 177,815 ms para 100, 1.000 y 10.000 filas. No es un SLA. El
experimento journal de diez repeticiones dio DELETE 0 commits/10 BUSY y WAL 10
commits/0 BUSY, integridad `ok`; no se cambió la política del producto.

## 5. Demos verificadas

| Dataset empacado | Esperado | Validador/API/navegador |
|---|---|---|
| 6 pedidos | 6 total, 2 válidas, 4 inválidas, 5 incidencias | Coincide |
| 100 pedidos | 100 total, 90 válidas, 10 inválidas, 10 incidencias | Coincide |

La demo de 6 muestra cinco códigos y enseña que una fila puede tener dos
incidencias. La demo de 100 tiene diez filas distintas con un correo sintético
inválido cada una. El navegador procesó ambas, mostró historial y recibió el
evento de descarga del CSV. La prueba API verificó contenido/BOM de exportación.

## 6. Matriz de cierre

| Criterio | Estado | Evidencia |
|---|---|---|
| API, perfiles, historial, detalle, páginas y exportación | PASS | 113 tests + smoke wheel |
| Demos 6/100 con resultados estables | PASS | prueba empacada/API/E2E |
| 2 MiB, request ASGI y 10.000 filas | PASS | regresiones límite exacto/+1 |
| Privacidad de filas/nombres | PASS | API + dump SQLite + navegador |
| SQLite, rollback, locks, 503, backup/restore | PASS | suite coordinada |
| Fuente limpia y wheel instalable | PASS | dos venvs aisladas |
| Assets del wheel | PASS | `importlib.resources` desde site-packages |
| Responsive 360/390/768/1366 | PASS | sin overflow de página |
| Teclado/labels/alertas/tacto | PASS básico | AX real, skip-link y 44 px |
| Python 3.11 | NO VERIFICADO | intérprete no instalado |
| Docker | NO VERIFICADO | comando no disponible; revisión estática |
| GitHub Actions | NO VERIFICADO | no existe remoto/publicación |
| Materiales de portafolio P1 | PASS | documentos ES/EN y guías |
| Identidad y licencia | PENDIENTE_DEL_AUTOR | no deben inventarse |

## 7. Riesgos residuales

- Sin autenticación, autorización, TLS, aislamiento de clientes, rate limiting
  distribuido, cifrado, retención, borrado o auditoría empresarial.
- SQLite admite una escritura efectiva; el contrato es un worker. WAL no se
  adopta sin pruebas de checkpoint, recuperación, filesystem y operación.
- El límite ASGI protege a la aplicación, pero un proxy/servidor futuro también
  tendría que limitar bytes antes de entregar chunks.
- La validación de correo es sintáctica y simple; las políticas monetarias son
  de demo, no reglas contables certificadas.
- No hubo pentest, SAST remoto, prueba Docker, CI remota ni verificación 3.11.
- “113 pruebas sin warnings” no significa ausencia total de defectos.

Por estos motivos el servicio no debe publicarse en Internet ni recibir datos
reales o sensibles.

## 8. Cómo iniciar, hacer clic y cerrar

```powershell
cd <RUTA_LOCAL>\DataTrust_API_Starter
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\scripts\iniciar_demo.ps1
```

1. Abrir `http://127.0.0.1:8000/` y comprobar “API local activa · v1.0.0”.
2. Descargar **Demo de 6 pedidos**, seleccionarla y pulsar **Validar archivo**.
3. Confirmar 6/2/4/5, revisar la tabla y pulsar **Exportar CSV seguro**.
4. Repetir con **Demo de 100 pedidos** y confirmar 100/90/10/10.
5. Cerrar con `Ctrl+C` en PowerShell.

## 9. Único trabajo pendiente para publicar

- [ ] Completar datos del autor.
- [ ] Elegir y añadir licencia.
- [ ] Configurar identidad Git elegida por el titular.
- [ ] Revisar privacidad y crear el primer commit.
- [ ] Crear el remoto y publicar conscientemente.
- [ ] Observar CI real 3.11/3.12; probar Docker si se desea citarlo.

No hay un nuevo ciclo funcional pendiente dentro de DataTrust.

## 10. Cuatro conceptos, explicados de forma simple

**API REST.** Es un contrato HTTP: cada ruta representa una operación y usa
códigos como 201, 404 o 422. Así, dashboard y otros clientes consumen la misma
lógica sin duplicarla.

**Validación de datos.** No es “arreglar” silenciosamente. Es comparar una
entrada con reglas explícitas y devolver evidencia: fila, campo, código y
mensaje. El archivo original permanece intacto.

**Pruebas automatizadas.** Son ejemplos ejecutables que convierten un requisito
en una comprobación repetible. Una prueba roja reprodujo la ausencia de cada
demo; solo después se añadió el recurso que la hizo verde.

**SQLite.** Es una base de datos transaccional almacenada en un archivo. Es
ideal para una demo local, pero coordina una sola escritura efectiva. Las
transacciones evitan guardar media ejecución y el timeout convierte contención
esperada en un error controlado.

## 11. Declaración de cierre

DataTrust API queda cerrada en v1.0.0. No se propone otra ampliación general.
Solo un defecto bloqueante concreto y reproducible debe reabrir la release; una
plataforma multiusuario, integración empresarial o proyecto de IA requiere un
objetivo independiente.
