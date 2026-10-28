# Changelog

Este archivo registra cambios verificables del prototipo. El proyecto continúa siendo una demo local y no se declara apto para producción.

## [1.0.0] - 2026-10-27

**Portfolio Local Release — Not Production Ready**

### Añadido
- Demos sintéticas empacadas de 6 pedidos (2 válidos, 4 inválidos, 5 incidencias) y 100 pedidos (90/10/10), con pruebas de recursos y flujo HTTP.
- Lanzador PowerShell local que exige una venv existente, usa `127.0.0.1` y un worker, sin descargar software ni cambiar políticas.
- Guías definitivas de usuario, reclutador, caso de estudio, CV/LinkedIn, publicación GitHub y cierre v1.
- Sección de autoría pública de Yerlan Daniel Gómez Hernández y transparencia sobre asistencia de herramientas de IA.
- Explicación visible de filas inválidas frente a incidencias y pista de desplazamiento horizontal para la tabla móvil.
- Publicación pública en `yerlangomezhernandez24-afk/datatrust-api`, rama `main`, con metadatos y temas técnicos revisados.

### Verificado localmente
- 113 pruebas descubiertas y aprobadas sin warnings; `compileall`, `node --check`, `pip check` y coherencia de versión correctos.
- Instalación editable limpia y wheel final instalados en entornos separados con Python 3.12.14.
- Wheel final de 32.718 bytes, SHA-256 `D445445C631713F17B0C80A2994B26801E45CDC7151192C426743618D1DA2A3E`, con metadata README, HTML, CSS, JS, SVG, perfiles y ambas demos.
- Smoke Uvicorn desde el wheel y E2E real: demos 6/100, error 422, selección de perfil, exportación, teclado y 360/390/768/1366 sin overflow de página.
- GitHub Actions completó correctamente la matriz Python 3.11/3.12; la segunda ejecución terminó verde en 27 s sin advertencias de runtimes Node obsoletos.

### Corregido tras publicar
- Workflow actualizado a `actions/checkout@v7` y `actions/setup-python@v7` para eliminar las advertencias de Node 20 observadas en la primera ejecución.

### Límites
- Python 3.11 no está instalado localmente, pero la matriz remota sí lo verificó.
- Docker continúa sin ejecutarse en este equipo y no se desplegó el servicio.
- No se añadió licencia; el titular todavía debe elegirla.

## [0.3.0] - 2026-10-27

### Añadido
- Dashboard local rediseñado con propuesta de valor, recorrido guiado, datos de prueba descargables, estado real de la API y layouts verificados en 360/390/768/1366 px.
- Middleware de encabezados defensivos, smoke HTTP con caso 413 y documentación de demo/cierre para portafolio.
- Regresiones para CSV vacío, MIME genérico válido, contenido no CSV, locks SQLite en lectura, mensajes de perfil desconocido y prefijos de fórmula con controles Unicode.

### Corregido
- Los locks SQLite agotados en lecturas se traducen a 503 con `Retry-After` en vez de 500; las conexiones siempre se cierran.
- Los mensajes de perfiles desconocidos ya no reflejan entrada arbitraria.
- La exportación detecta prefijos de fórmula incluso tras controles/formato, sin modificar los datos originales almacenados.
- Controles táctiles, texto singular/plural, paginación del dashboard y encabezados defensivos del HTML/API.
- T-109 local en Python 3.12: metadata editable coherente y TestClient migrado/validado con `httpx2` sin warnings.

### Verificado localmente
- 109 pruebas aprobadas sin warnings, `compileall`, `pip check`, sintaxis JavaScript, smoke Uvicorn, navegador E2E y benchmark reproducible.
- Python 3.11, Docker y GitHub Actions remotos siguen sin ejecución disponible en este equipo.

## [0.2.1] - 2026-10-27

### Añadido
- Política de datos con límites de encabezados/campos en caracteres y bytes, identificadores Unicode e importes `Decimal` por rango/escala/moneda.
- Backup, restauración a destino nuevo e integridad SQLite estructural/referencial mediante API nativa y CLI local.
- Experimento reproducible DELETE/WAL, smoke HTTP con Uvicorn real y recorrido de demo de tres minutos.
- Check de consistencia de versión para fuente y metadata instalada; estrategia de dependencias documentada.

### Corregido
- Signos positivos, notación científica, escala excesiva, formatos incompletos e importes fuera de rango ya no se aceptan.
- Campos mayores al límite implícito del parser llegan a una política explícita y mensajes neutros.
- Identificadores con controles/formato invisibles se rechazan; headers tienen normalización/límite definidos.
- Dashboard anuncia errores/busy/selección y deja de desbordar horizontalmente a 390 px.
- El experimento SQLite cierra explícitamente conexiones; el primer intento dejó un temporal bloqueado en Windows y no se usó como evidencia.

### Verificado localmente
- Suite base 74 casos; cierre v0.2.1 con 105 casos verdes y una advertencia visible.
- Browser E2E local, smoke HTTP, CLI backup/restauración, sintaxis JavaScript y experimento SQLite ejecutados.

### Pendiente
- Advertencia de transición `httpx`/`httpx2`, Python 3.11, GitHub Actions remoto y Docker continúan no verificados en esta plataforma.

## [0.2.0] - 2026-10-26

### Añadido
- Perfiles JSON locales `orders_v1` y `orders_usd_v1`, con schema estricto, ids versionados y registro permitido.
- `GET /api/v1/profiles` y selección `profile` al cargar CSV.
- `GET /api/v1/runs/{id}/issues.csv`: streaming completo UTF-8, nombre neutro y protección de todas las celdas frente a fórmulas.
- Dashboard local real en `/` con carga, perfil, métricas, historial, detalle paginado y descarga.
- Benchmark reproducible T-104, snapshot de constraints Python 3.12, matriz CI 3.11/3.12 y SECURITY.md.
- Diseños explícitos —no simulaciones— para idempotencia y experimento ML futuro.

### Verificado localmente
- Pruebas de perfiles desconocidos, JSON inválido/duplicado, exportación de más de 100 incidencias, Unicode/comillas/saltos y formula injection.
- Integración del flujo completo usado por el dashboard y sintaxis JavaScript con Node.
- Benchmark del validador puro para 100, 1.000 y 10.000 filas.

### No verificado
- Docker build/run (comando no instalado), GitHub Actions remoto, navegador E2E, pentest y ML.

### Resultado final local
- Suite completa: 74 pruebas aprobadas, una advertencia visible, ninguna omitida ni fallida.
- `compileall`, `pip check` y sintaxis JavaScript terminaron correctamente.
- Informe reproducible de implementación, riesgos y reanudación en `docs/INFORME_FINAL_CODEX.md`.

## [0.1.3] - 2026-10-25

### Añadido
- Middleware ASGI que limita el cuerpo HTTP completo antes del parser multipart mediante conteo de chunks reales.
- Configuración `DATATRUST_MAX_REQUEST_BYTES`, separada del máximo CSV de 2 MiB.
- Pruebas de requests fragmentados, `Content-Length` ausente/falso, rechazo temprano y límite exacto.
- Escenario lector/escritor SQLite controlado además de las escrituras concurrentes.

### Seguridad local
- El middleware responde 413 sin persistencia parcial y no usa `Content-Length` como única defensa.
- Dockerfile preparado para usuario no root, almacenamiento con permisos y un solo worker. Docker no estaba instalado en el entorno de verificación, por lo que la imagen no fue construida ni ejecutada.

## [0.1.2] - 2026-10-25

### Corregido
- Los `order_id` Unicode canónicamente equivalentes (NFC/NFD) se detectan como duplicados.
- Los correos con caracteres invisibles de control o formato se marcan como inválidos.
- El timeout de escritura SQLite quedó explícito en 5 segundos; un bloqueo agotado revierte la transacción y responde HTTP 503 con `Retry-After`, en lugar de HTTP 500.

### Pruebas
- Límites exactos de 2 MiB y 10.000 filas, además de un byte y una fila adicionales.
- Diferencia entre tamaño del archivo CSV y tamaño total multipart.
- UTF-8, BOM, Unicode válido, encoding inválido, esquemas alternativos, CSV mal formado, fechas e importes extremos.
- Paginación real de ejecuciones e incidencias, privacidad integral y prefijos de fórmula.
- Escrituras SQLite simultáneas, espera por bloqueo, liberación controlada y timeout sin persistencia parcial.

### Documentación
- Riesgo pendiente de cuerpos HTTP procesados antes del límite del endpoint.
- Política propuesta de WAL, `busy_timeout`, transacciones, un worker y migración futura.
- Riesgo de inyección de fórmulas reservado para la futura exportación; no se alteran datos de entrada indiscriminadamente.

## [0.1.1] - 2026-10-25

### Corregido
- Validación de la extensión completa antes de tratar nombres largos; se rechazan sufijos disfrazados como `.csv.exe`.
- Límite superior de `offset` compatible con enteros SQLite para evitar respuestas HTTP 500.
- Cierre explícito de conexiones SQLite después de commit o rollback, incluso cuando una escritura falla.
- Rechazo claro de SQLite `:memory:`, que no es compatible con una conexión nueva por operación.
- Validación CSV y escritura SQLite delegadas al threadpool desde el endpoint asíncrono.

### Privacidad
- El nombre original de la carga ya no se almacena ni se devuelve. El contrato conserva `filename` como nombre técnico `<run_id>.csv`.

### Pruebas
- Regresiones para nombres largos, extensiones disfrazadas, privacidad del nombre, offset fuera de rango, configuración en memoria, threadpool, cierre de conexiones y rollback.

## [0.1.0] - 2026-10-25

### Añadido
- MVP local con FastAPI, perfil fijo `orders_v1`, reglas deterministas, SQLite, ejemplos sintéticos, pruebas automatizadas y configuración de CI.
