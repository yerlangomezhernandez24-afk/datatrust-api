# Backlog de desarrollo y aprendizaje con Codex

## Versión v1.0.0 — cierre de portafolio local

- [x] Incorporar y probar demos empacadas de 6 y 100 pedidos con resultados deterministas.
- [x] Verificar instalación limpia desde fuente y desde wheel en entornos separados.
- [x] Comprobar recursos empacados, smoke HTTP, versión y dependencias.
- [x] Ejecutar E2E real en 360/390/768/1366, caso nominal, error, teclado y exportación.
- [x] Preparar documentación ES/EN, usuario, reclutador, caso de estudio, CV y publicación.
- [x] Congelar alcance como **Portfolio Local Release — Not Production Ready**.

No existe un siguiente hito general de DataTrust. Las listas futuras que se
conservan más abajo son decisiones históricas o posibles productos distintos,
no tareas activas. Solo un defecto bloqueante y reproducible debe reabrir esta
release.

## Versión v0.1 — Completada en código; validar localmente antes de publicar
- [x] Documentar problema, usuario, hipótesis, alcance y limitaciones.
- [x] Implementar lectura de CSV UTF-8 y perfil orders_v1.
- [x] Validar requeridos, duplicados, email, amount, currency y order_date.
- [x] Registrar metadatos e incidencias en SQLite.
- [x] Exponer endpoints REST y OpenAPI.
- [x] Preparar pruebas pytest y workflow CI (ejecución local verificada; ejecución remota pendiente).
- [x] Crear ejemplos sintéticos y Dockerfile para pruebas locales.

## Versión v0.1.1 — Estabilización completada localmente
- [x] Validar la extensión real antes de cualquier tratamiento del nombre y cubrir nombres largos/extensiones disfrazadas.
- [x] Sustituir nombres originales por identificadores técnicos neutrales en API y SQLite.
- [x] Acotar `offset` al rango entero de SQLite para responder HTTP 422 en entradas fuera de rango.
- [x] Cerrar explícitamente todas las conexiones, conservando commit/rollback.
- [x] Rechazar SQLite `:memory:` con un error claro al iniciar.
- [x] Delegar validación y escritura SQLite del POST al threadpool.
- [x] Añadir pruebas de regresión y actualizar documentación/changelog.

## Versión v0.1.2 — T-105 y confiabilidad completadas localmente
- [x] Probar los límites exactos de 2 MiB y 10.000 filas, además de un byte/una fila adicionales.
- [x] Distinguir bytes del CSV y tamaño multipart; documentar que falta un límite de transporte previo al parser.
- [x] Cubrir UTF-8, BOM, Unicode, codificación inválida, variantes de esquema, datos malformados, fechas e importes extremos.
- [x] Probar paginación con datos reales y límites de `limit`/`offset`.
- [x] Verificar que nombres sensibles, valores crudos y prefijos de fórmula no se persisten ni se exponen.
- [x] Probar escrituras simultáneas y bloqueos SQLite controlados sin esperas aleatorias.
- [x] Normalizar ID Unicode equivalentes, rechazar controles en email y responder 503 ante bloqueo agotado.

## Versión v0.1.3 — límites de transporte y política SQLite
- [x] **T-106** Limitar el cuerpo HTTP antes del parser multipart mediante conteo real de bytes en ASGI; no confiar solo en `Content-Length`.
- [x] Probar request fragmentado, cabecera ausente/incorrecta, límite exacto y ausencia de persistencia parcial.
- [x] Probar lector/escritor y escritores concurrentes; declarar timeout, `workers=1`, respuesta 503 y umbral conceptual de migración.
- [x] **T-107** Evaluar WAL en filesystem local y recuperación; evidencia registrada y decisión de conservar DELETE/un worker.
- [x] **T-108** Definir longitud máxima de campo, filas vacías, caracteres invisibles en identificadores y precisión/escala/notación permitida para importes.
- [x] Fijar un snapshot de constraints reproducible para el entorno Python 3.12 observado y matriz CI 3.11/3.12.
- [x] **T-109 local 3.12** Resolver la advertencia TestClient/HTTPX sin ocultarla mediante `httpx2` y metadata coherente.
- [ ] **T-109 externo** Verificar Python 3.11 y la matriz CI remotamente cuando el titular publique.

## Versión v0.2.1 — confiabilidad local
- [x] Política de datos explícita con límites por campo y reglas monetarias exactas.
- [x] Backup/restauración mediante API SQLite, destinos no sobrescritos e integridad estructural/referencial.
- [x] Experimento DELETE/WAL reproducible sin cambiar el journal del producto.
- [x] Smoke HTTP Uvicorn real y navegador E2E local con datos sintéticos.
- [x] Accesibilidad básica y corrección de overflow móvil a 390 px.
- [x] Check de versión fuente/paquete/API y verificación instalada preparada para CI.
- [x] T-109 local en Python 3.12: `httpx2` y metadata instalada validados sin warnings.
- [ ] Python 3.11 y CI remoto permanecen sin ejecución disponible.

## Versión v0.3.0 — cierre de calidad y presentación local
- [x] Traducir locks SQLite de lectura/escritura a 503 y cerrar conexiones en todas las rutas.
- [x] Evitar reflexión de perfiles desconocidos y ampliar protección de exportación ante controles invisibles.
- [x] Añadir encabezados defensivos y ampliar el smoke HTTP con 413/sin persistencia.
- [x] Rediseñar dashboard, ejemplo descargable, ayuda, singular/plural y controles táctiles.
- [x] Verificar E2E en navegador real y 360/390/768/1366 px sin overflow horizontal.
- [x] Cerrar documentación ES/EN, demo de reclutador, evidencia y reporte honesto.

## Versión v0.2.0 — valor operacional local
- [x] **T-101** Perfiles JSON locales, versionados y de lista permitida, sin ejecución arbitraria ni rutas de cliente.
- [x] **T-102** Descarga CSV completa de incidencias con streaming y protección frente a inyección de fórmulas.
- [ ] **T-103** Operaciones idempotentes por hash: diseño documentado; bloqueado hasta definir identidad/privacidad/retención.
- [x] **T-104** Benchmark repetible y ejecutado para 100, 1.000 y 10.000 filas con hardware/metodología reales.
- [x] **T-105** Tests para inyección CSV, codificaciones inválidas, Unicode, columnas extra y límites (completado en v0.1.2).

## Preparación piloto futura
- [x] **T-201** Dashboard local conectado para cargas, perfiles, historial, paginación y descarga.
- [ ] **T-202** Configuración de reglas por perfil sin programar, con controles de acceso.
- [ ] **T-203** Políticas de retención, eliminación, logs auditables y autenticación (antes de uso real).
- [ ] **T-204** Entrevistas y pruebas observadas con usuarios voluntarios usando datos sintéticos.

## Especialización IA — v0.4, solo después de tener baseline
- [ ] **T-301** Modelo local de anomalías (IsolationForest u otro) sobre datos sintéticos/públicos apropiados.
- [ ] **T-302** Comparación reproducible contra reglas deterministas; matriz de confusión, precision/recall; evitar data leakage.
- [ ] **T-303** Explicaciones de anomalías con trazabilidad; ninguna decisión irreversible sin supervisión.

## Evidencia para CV
README claro, OpenAPI, dashboard conectado, tests verdes, ejemplos sintéticos, benchmark reproducible y explicación de decisiones. Capturas, Docker y CI remoto solo podrán citarse cuando se obtengan realmente. No afirmar uso empresarial.
