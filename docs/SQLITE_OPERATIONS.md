# Operación local de SQLite — backup, restauración y journal

DataTrust API v1.0.0 continúa soportando **un proceso/worker, filesystem local y cargas pequeñas**. Estas herramientas no convierten SQLite en un sistema multiusuario ni sustituyen una política empresarial de backups.

## Política activa

- Una conexión por operación y cierre explícito.
- `PRAGMA foreign_keys=ON` en las conexiones de la aplicación.
- Transacción única para ejecución + incidencias.
- Timeout de lock de cinco segundos; al agotarse, rollback y HTTP 503.
- Journal del producto: valor predeterminado de SQLite (`DELETE` en el entorno verificado).
- `synchronous=FULL` observado; el código no lo reduce.
- Un worker soportado. No se promete más de un writer simultáneo.

## Verificar integridad

```powershell
.\.venv\Scripts\python.exe scripts\sqlite_maintenance.py check .\data\datatrust.sqlite3
```

El comando abre una base existente, ejecuta `PRAGMA integrity_check` y `PRAGMA foreign_key_check`, y no crea una base si la ruta es incorrecta.

## Crear un backup consistente

Detén escrituras de aplicación cuando sea práctico y elige un destino **nuevo**:

```powershell
.\.venv\Scripts\python.exe scripts\sqlite_maintenance.py backup `
  .\data\datatrust.sqlite3 `
  .\backups\datatrust-2026-10-27.sqlite3
```

La herramienta:

1. verifica la integridad de origen;
2. reserva el destino con creación exclusiva;
3. usa `sqlite3.Connection.backup()`, que genera una vista consistente incluso con una conexión lectora abierta;
4. verifica el resultado y reporta número de páginas;
5. nunca reemplaza un archivo preexistente.

No copies a ciegas una base activa con `Copy-Item`: en especial con WAL podrían existir cambios necesarios en `-wal`/`-shm`.

## Restaurar sin sobrescribir

Primero conserva la base activa. Restaura siempre hacia otra ruta nueva y valida la aplicación contra esa copia:

```powershell
.\.venv\Scripts\python.exe scripts\sqlite_maintenance.py restore `
  .\backups\datatrust-2026-10-27.sqlite3 `
  .\recovery\datatrust-restored.sqlite3

$env:DATATRUST_DB = (Resolve-Path .\recovery\datatrust-restored.sqlite3)
.\.venv\Scripts\python.exe -m uvicorn datatrust_api.main:app `
  --host 127.0.0.1 --port 8001 --workers 1
```

Comprueba `/health`, historial y una exportación usando solo datos sintéticos. La herramienta se niega a sobrescribir el destino; sustituir una base real sigue siendo una decisión manual del titular fuera de este procedimiento automatizado.

## Experimento DELETE frente a WAL

Comando ejecutado el 27 de octubre de 2026:

```powershell
.\.venv\Scripts\python.exe scripts\benchmark_sqlite_journal.py --repeats 20
```

Escenario determinista: una conexión mantiene una transacción lectora; otra usa `BEGIN IMMEDIATE`, inserta una fila sintética e intenta confirmar con timeout cero. No usa sleeps aleatorios.

| Modo | Journal real | Commits | `BUSY` | Mediana del intento | Integridad |
|---|---|---:|---:|---:|---|
| DELETE | `delete` | 0/20 | 20/20 | 0,495750 ms | 20/20 `ok` |
| WAL | `wal` | 20/20 | 0/20 | 10,856050 ms | 20/20 `ok` |

Entorno: Windows 11 build 26200, Python 3.12.14, SQLite 3.53.1 y `synchronous=2` (`FULL`). La duración de un fallo rápido no es comparable con el tiempo de un commit exitoso; la evidencia útil es funcional: WAL permitió el commit con el lector activo en este escenario local.

## Decisión vigente en v1.0.0

**No se activa WAL automáticamente.** La evidencia muestra una ventaja lector/writer, pero el producto sigue usando un worker y carga pequeña. Cambiar el journal de bases existentes agrega sidecars, requisitos de checkpoint, recuperación y empaquetado que todavía no se han probado en Docker, filesystems de red o cierres abruptos. El backup usa la API SQLite y es compatible con una futura evaluación WAL.

Reevaluar WAL solo si una carga representativa demuestra locks frecuentes y después de probar checkpoint, recuperación tras terminación, backup activo y volumen persistente. Si el objetivo requiere varios workers o escritura sostenida, la opción preferible es diseñar una migración a PostgreSQL, no prometer writers SQLite paralelos.

## Repetición de cierre v1.0.0

El mismo escenario se ejecutó con 10 repeticiones el 27 de octubre de 2026:

| Modo | Commits | `BUSY` | Mediana | Integridad |
|---|---:|---:|---:|---|
| DELETE | 0/10 | 10/10 | 0,512150 ms | `ok` |
| WAL | 10/10 | 0/10 | 10,529400 ms | `ok` |

El resultado funcional coincide con el experimento anterior y no cambia la
decisión: no se modifica el journal automáticamente en esta release congelada.
