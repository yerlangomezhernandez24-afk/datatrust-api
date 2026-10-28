# Diseño pendiente T-103 — idempotencia por hash

Estado: **PENDIENTE; no implementado en v0.2.0**.

## Por qué no se añadió un atajo

Responder con una ejecución previa al reconocer un hash puede revelar que otro usuario futuro ya procesó el mismo archivo. También debe definirse si el resultado sigue siendo equivalente cuando cambia el perfil, su versión, una regla o el software. Sin autenticación/tenant y retención, una deduplicación global sería una mala frontera de privacidad.

## Política propuesta

- Clave lógica: SHA-256 de `bytes_csv || id_perfil || versión_perfil || versión_configuración` con codificación canónica y separación inequívoca de componentes.
- Alcance futuro: por tenant autenticado, nunca global entre clientes.
- Respuesta: distinguir reintento idempotente de consulta histórica; no confirmar existencia a un actor sin permiso.
- Retención: el índice de hashes debe caducar/eliminarse con la ejecución asociada.
- Concurrencia: columna/tabla con restricción `UNIQUE(tenant_id, fingerprint)` y una transacción `INSERT ... ON CONFLICT`, seguida de lectura del ganador. Un lock de proceso no basta con varios workers.
- Privacidad: almacenar solo el digest, nunca bytes del archivo, pero tratar el digest como metadato potencialmente sensible.
- Compatibilidad: una migración versionada y reversible debe preservar las ejecuciones existentes sin inventar fingerprints retroactivos.

## Pruebas necesarias antes de implementar

1. Dos solicitudes concurrentes idénticas crean una sola ejecución coherente.
2. Mismos bytes con perfiles/versiones distintas crean ejecuciones distintas.
3. Fallo tras reservar fingerprint no deja una entrada huérfana.
4. Un usuario/tenant no puede descubrir resultados de otro.
5. Eliminación/retención elimina también el índice.

La decisión debe retomarse después de diseñar identidad, autorización y retención; por eso no bloquea el portafolio local actual.
