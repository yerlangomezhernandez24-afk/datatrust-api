# PRD — DataTrust API v1.0.0

**Estado:** Portfolio Local Release — Not Production Ready; alcance general congelado el 27 de octubre de 2026.

## 1. Problema e hipótesis

Equipos pequeños que reciben CSV necesitan detectar datos incompletos o mal formados antes de importarlos. Hipótesis pendiente de validar: una API con motivos claros y una UI simple puede reducir la revisión manual de conjuntos pequeños.

No se ha probado con empresas reales. No existen cifras de ahorro, adopción ni exactitud fuera de las reglas documentadas.

## 2. Usuario inicial

Analista de operaciones o desarrollador backend que trabaja localmente con pedidos sintéticos y necesita un resultado reproducible por fila/campo.

## 3. Funciones implementadas

- Recepción CSV UTF-8: archivo máximo 2 MiB, request multipart con límite ASGI separado y máximo 10.000 registros.
- Perfiles locales `orders_v1` y `orders_usd_v1`, definidos en JSON estricto y seleccionables sin rutas/código arbitrario.
- Reglas permitidas: requerido, límites de caracteres/bytes, identificadores sin controles invisibles, unicidad NFC/casefold, email básico, importe Decimal por rango/escala, enumeración y fecha ISO real.
- SQLite de metadatos/incidencias sin nombre original ni valores crudos de filas.
- Historial, detalle, paginación y exportación completa de incidencias.
- Exportación CSV con neutralización de fórmulas y nombre de descarga neutro.
- Dashboard local conectado para cargar, seleccionar perfil, consultar, paginar y descargar.
- Datos sintéticos, pruebas automatizadas, benchmark reproducible y configuración CI 3.11/3.12.
- Backup/restauración SQLite sin sobrescritura, verificación de integridad, smoke HTTP real y demo de navegador.
- Dashboard orientado a evaluación de portafolio con estado de salud, datos sintéticos descargables, ayuda de errores y respuesta responsive.
- Encabezados HTTP defensivos y traducción uniforme de locks SQLite esperados a 503.
- Escenarios descargables y empacados de 6 pedidos (6/2/4/5) y 100 pedidos (100/90/10/10), con resultados protegidos por pruebas.

## 4. Criterios de aceptación verificados

- Archivo válido retorna 201, ID UUID, perfil y conteos correctos.
- Archivo de 2 MiB/10.000 filas se acepta; un byte/una fila adicional se rechaza sin persistencia parcial.
- El límite ASGI cuenta chunks reales y responde 413 con `Content-Length` ausente, inválido o falsamente bajo.
- Extensión real distinta de `.csv` retorna 415; schema/encoding incompatible retorna 422.
- Duplicados canónicamente equivalentes, email con controles, fechas imposibles, enum desconocido e importes no finitos generan incidencias estáticas.
- Nombre original y valores de filas/correos/importes no aparecen en API ni SQLite.
- Paginación valida rangos SQLite y no produce 500 por offset extremo.
- Las conexiones cierran tras éxito/error; las transacciones revierten completas y un lock agotado retorna 503.
- El detalle muestra hasta 100 incidencias; la exportación transmite todas y protege `=`, `+`, `-`, `@` tras whitespace.
- Perfil desconocido/ruta simulada retorna 422 sin persistir; JSON local con claves/reglas inválidas se rechaza.
- Dashboard y assets se sirven localmente y su flujo backend completo está cubierto por integración.
- Signos, exponente, coma, más de dos decimales e importes fuera de 0.01–999999999999.99 se rechazan sin redondeo.
- Backup/restauración preserva un snapshot consistente en una base nueva y verifica integridad estructural/referencial.
- Smoke Uvicorn real recorre flujo HTTP en loopback; el navegador verificó carga, error, descarga, teclado y breakpoint móvil.
- Instalación limpia y wheel 1.0.0 comprobados en entornos distintos; 113 pruebas finales aprobadas sin warnings.

## 5. Restricciones y diseño responsable

- Presupuesto de APIs/nube: $0; no se requieren claves.
- Solo datos sintéticos. El sistema minimiza persistencia, pero no es una plataforma regulada.
- Uvicorn en `127.0.0.1`, un worker y SQLite en filesystem local.
- No se promete disponibilidad, escalabilidad, detección total de errores ni seguridad de producción.
- Benchmark publicado solo para el validador puro y el hardware medido.

## 6. Fuera de alcance actual

- Autenticación, autorización, tenants, TLS gestionado, cifrado en reposo, planificación externa de backups, retención/borrado, rate limiting distribuido y despliegue público.
- Schema totalmente arbitrario, reglas con código, ERP/OCR, procesamiento masivo o multiworker.
- Idempotencia por hash hasta definir identidad/privacidad/retención.
- ML activo. Solo hay una propuesta experimental y no se instalaron dependencias ni se inventaron métricas.

## 7. Métricas y evidencia

- Suite local, benchmark T-104 y comandos reales: `VERIFICACION.md` y `BENCHMARK.md`.
- GitHub Actions solo está configurado; no se observó ejecución remota.
- Dockerfile fue endurecido, pero Docker no estaba instalado y no se construyó la imagen.
- Python 3.11 y CI remoto continúan sin ejecución observada; la instalación limpia local solo verificó Python 3.12.14.

## 8. Validación pendiente con usuarios

- Entrevistar voluntariamente a tres analistas/desarrolladores usando datos sintéticos.
- Observar carga, selección de perfil, interpretación y descarga sin dar instrucciones durante la tarea.
- Medir errores de comprensión, tiempo de tarea y reglas realmente frecuentes.
- Decidir después si priorizar retención/autenticación, más perfiles o migración de almacenamiento.

Esta investigación no forma parte del cierre v1.0.0. Cualquier continuación debe abrir un alcance nuevo basado en evidencia, no una ampliación automática de esta demo.
