# Demo local de 3 minutos para reclutadores

Objetivo: demostrar una API de calidad de datos, una UI conectada, decisiones de privacidad y pruebas reproducibles. Usa únicamente los ejemplos sintéticos incluidos.

## 0:00–0:45 · Preparar y verificar

En PowerShell, desde la raíz:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m uvicorn datatrust_api.main:app `
  --host 127.0.0.1 --port 8000 --workers 1
```

Explica que `127.0.0.1` evita exponer la demo a la red y que SQLite soporta un worker en este alcance.

## 0:45–1:45 · Validar desde el dashboard

1. Abre `http://127.0.0.1:8000/`.
2. Elige `orders_v1`.
3. Carga `examples/orders_with_issues.csv`.
4. Muestra los conteos, el historial y las incidencias.

El ejemplo contiene 6 filas sintéticas, 2 válidas, 4 inválidas y 5 incidencias con el perfil base. Señala que el nombre original y los valores de las filas no se guardan: la ejecución usa un UUID y persiste solo mensajes estáticos.

## 1:45–2:20 · Perfil y exportación

1. Repite la carga con `orders_usd_v1` para mostrar que un perfil local cambia una regla sin ejecutar código aportado por el cliente.
2. Descarga `validation-issues.csv`.
3. Explica que se transmiten todas las incidencias por streaming, mientras el detalle normal limita a 100.
4. Explica la neutralización de `=`, `+`, `-` y `@` en la salida para reducir formula injection.

## 2:20–3:00 · Arquitectura y evidencia

- Abre `/docs` para enseñar OpenAPI.
- Resume las capas: FastAPI/ASGI, perfiles JSON permitidos, validador puro y SQLite parametrizado.
- Menciona límites exactos: request ASGI, archivo 2 MiB, 10.000 filas, longitud por campo e importes con `Decimal`.
- Enseña `docs/VERIFICACION.md` y `docs/SQLITE_OPERATIONS.md` como evidencia de pruebas, backup y decisión WAL.
- Cierra indicando límites honestos: sin autenticación, tenants, retención ni publicación; no es producción.

## Recorrido manual de accesibilidad

- Navega con `Tab` y comprueba que el foco sea visible.
- Verifica etiquetas del perfil y archivo, enlace de salto, encabezados de tabla y estados anunciados.
- Reduce la ventana a unos 390 px: los paneles deben ocupar una columna y la página no debe crear scroll horizontal; la tabla conserva su propio desplazamiento.
- Carga un archivo no CSV sintético: el error debe mostrarse y anunciarse como alerta sin ruta local, stack trace ni contenido.

## Verificación HTTP automática equivalente

```powershell
.\.venv\Scripts\python.exe scripts\smoke_http_e2e.py
```

El script inicia Uvicorn en un puerto aleatorio de `127.0.0.1`, usa una base temporal, recorre health/UI/perfiles/carga/listado/detalle/paginación/exportación/404, detiene el proceso y elimina el temporal.
