# Seguridad y alcance responsable

## Estado soportado

DataTrust API v1.0.0 es una demostración local y educativa: **Portfolio Local Release — Not Production Ready**. No está diseñada para exponerse a Internet ni para procesar datos personales, financieros o empresariales reales. No incluye autenticación, autorización, separación por organización, cifrado en reposo, retención, borrado verificable, rate limiting distribuido ni auditoría empresarial.

## Uso local recomendado

- Iniciar Uvicorn en `127.0.0.1` y mantener un solo worker mientras se utilice SQLite.
- En Docker, publicar únicamente con `-p 127.0.0.1:8000:8000`; `EXPOSE` no publica el puerto por sí mismo.
- Usar exclusivamente datos sintéticos. El nombre original y las filas del CSV no se conservan, pero la seguridad real exige más que minimizar persistencia.
- Mantener `DATATRUST_DB` en un directorio local con permisos del usuario. No usar filesystem de red sin evaluar locks y durabilidad.
- No añadir secretos al repositorio. `.env`, claves, certificados, bases y sidecars SQLite están ignorados, pero `.gitignore` no sustituye una revisión antes de publicar.

## Controles presentes

- Límite ASGI del cuerpo HTTP antes del parser multipart y límite separado de 2 MiB para el archivo.
- Máximo de 10.000 filas, perfil local permitido y validación de esquema/reglas.
- Límites explícitos de encabezados/campos, rechazo de identificadores invisibles y política monetaria Decimal sin redondeo silencioso.
- SQL parametrizado, transacciones cortas, cierre explícito y `foreign_keys=ON`.
- Timeout SQLite finito; locks agotados producen 503 sin persistencia parcial.
- Mensajes de incidencias estáticos, nombres técnicos neutrales y ausencia de filas originales en SQLite.
- Exportación CSV que neutraliza prefijos de fórmula en todas las celdas.
- Dashboard sin CDN y con política CSP básica en el documento principal.
- Respuestas con `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY` y `Referrer-Policy: no-referrer`.
- Backup/restauración local mediante API SQLite, integridad estructural/referencial y destinos que no se sobrescriben.

## Limitaciones conocidas

- Un servidor ASGI/proxy puede almacenar un chunk antes de entregarlo a la aplicación; el límite debe repetirse en la infraestructura si algún día existe un despliegue controlado.
- SQLite admite una sola escritura efectiva a la vez. WAL no está activado y varios workers no están soportados por este MVP.
- El rango/escala monetaria actual es una política de demo; debe reemplazarse con requisitos contables y de moneda validados antes de un uso real.
- `httpx2` fue validado localmente con Starlette/TestClient en Python 3.12; Python 3.11 y CI remota siguen pendientes de evidencia.
- No se ha realizado pentest, auditoría externa, análisis SAST remoto, build Docker ni ejecución de CI en GitHub. La prueba de navegador local no equivale a esas auditorías.

## Reporte de vulnerabilidades

No existe aún un canal público porque el proyecto no se ha publicado. Si el titular decide publicarlo, debe crear primero un canal privado de reporte y una política de versiones soportadas. No incluyas datos sensibles, credenciales ni archivos reales en un reporte.
