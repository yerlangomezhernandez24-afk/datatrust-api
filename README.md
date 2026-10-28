# DataTrust API · v1.0.0

**Portfolio Local Release — Not Production Ready**

DataTrust API es un proyecto personal y educativo de Ingeniería de Software y
Automatización. Valida archivos CSV de pedidos con reglas deterministas,
explica cada problema y permite exportar las incidencias. Funciona de forma
local con datos sintéticos: no usa IA, servicios de pago ni APIs externas.

[English overview](README.en.md) · [Guía de usuario](docs/GUIA_DEMO_USUARIO.md) ·
[Caso de estudio](docs/CASO_DE_ESTUDIO_PORTAFOLIO.md) · [Informe de cierre](docs/INFORME_CIERRE_DATATRUST_V1_CODEX.md)

## Problema y valor

Una importación de pedidos puede fallar tarde por identificadores duplicados,
correos inválidos, importes fuera de política, monedas inesperadas o fechas
imposibles. Este prototipo adelanta esa revisión y entrega un diagnóstico
reproducible antes de conectar los datos con otro sistema.

Está pensado para estudiantes, revisores técnicos y equipos pequeños que
quieran explorar calidad de datos localmente. Su valor demostrable es:

- reglas explícitas y versionadas, sin decisiones opacas;
- resumen de filas válidas e inválidas y detalle de incidencias;
- historial local y exportación CSV protegida contra fórmulas;
- minimización de datos: no persiste filas originales ni nombres originales;
- pruebas automatizadas de límites, privacidad, Unicode, SQLite y HTTP real.

No existen clientes, ahorro económico ni uso empresarial real declarados.

## Recorrido de la demo

1. El usuario elige `orders_v1` o `orders_usd_v1`.
2. La API recibe un CSV UTF-8 y valida estructura, tamaño y reglas de cada fila.
3. SQLite guarda solo un resumen técnico y las incidencias, nunca las filas.
4. El dashboard muestra métricas, historial, paginación y una exportación segura.

Una **fila inválida** puede contener varias **incidencias**. Por ejemplo, una
misma fila puede tener moneda y fecha inválidas; por eso ambos números no
siempre coinciden.

## Arquitectura y stack

```text
Navegador local
  └── FastAPI / Starlette (HTTP, ASGI, dashboard estático)
        ├── profiles.py + JSON (perfiles permitidos)
        ├── validator.py (reglas puras y Decimal)
        ├── store.py (consultas parametrizadas y transacciones)
        └── SQLite (resúmenes e incidencias)
```

- Python 3.11 o superior; cierre local comprobado con Python 3.12.14.
- FastAPI 0.162.0, Starlette 1.10.0, Uvicorn 0.54.0 y Pydantic 2.14.1.
- SQLite 3.53.1 en la verificación final.
- HTML, CSS y JavaScript sin framework de frontend.
- pytest 9.1.1 y httpx2 2.16.0 para pruebas.

## Límites reales

- CSV: hasta **2 MiB** y **10.000 filas de datos**.
- Cuerpo multipart: límite ASGI predeterminado de 2 MiB + 64 KiB para permitir
  la envoltura HTTP. El archivo sigue limitado exactamente a 2 MiB.
- Codificación UTF-8; se admite BOM UTF-8.
- SQLite en archivo, un proceso y `--workers 1`.
- Un usuario local; sin autenticación, autorización, TLS ni aislamiento.
- Sin cifrado en reposo, retención/borrado empresarial ni migraciones.
- Extensión y MIME son señales; la estructura CSV y las reglas son la autoridad.

## Inicio rápido en Windows PowerShell

Desde una copia local del proyecto:

```powershell
cd <RUTA_LOCAL>\DataTrust_API_Starter
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest -q
.\scripts\iniciar_demo.ps1
```

El script no descarga software ni cambia la política de PowerShell. Si tu
entorno no permite ejecutarlo, inicia con el comando equivalente:

```powershell
.\.venv\Scripts\python.exe -m uvicorn datatrust_api.main:app --host 127.0.0.1 --port 8000 --workers 1
```

Abre `http://127.0.0.1:8000/`. Para cerrar, vuelve a PowerShell y presiona
`Ctrl+C`.

Para reproducir exactamente el entorno verificado con Python 3.12:

```powershell
.\.venv\Scripts\python.exe -m pip install -c constraints\verified-py312.txt -e ".[dev]"
```

## Inicio en macOS o Linux

```bash
cd /ruta/local/DataTrust_API_Starter
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m pytest -q
.venv/bin/python -m uvicorn datatrust_api.main:app --host 127.0.0.1 --port 8000 --workers 1
```

La ejecución macOS/Linux no fue verificada en este cierre; CI mantiene una
matriz declarada para 3.11/3.12, pero no se ejecutó remotamente.

## Datos sintéticos incluidos

Los dos archivos se descargan desde el dashboard y también están empacados en
el wheel:

| Archivo | Perfil | Total | Válidas | Inválidas | Incidencias |
|---|---|---:|---:|---:|---:|
| `static/demo-orders-6.csv` | `orders_v1` | 6 | 2 | 4 | 5 |
| `static/demo-orders-100.csv` | `orders_v1` | 100 | 90 | 10 | 10 |

La muestra de 6 incluye duplicado, correo, importe, moneda y fecha inválidos.
La de 100 contiene 90 filas válidas y 10 correos sintéticos inválidos, uno por
fila. Todos los correos usan el dominio reservado `example.invalid`.

## API

| Método y ruta | Resultado |
|---|---|
| `GET /` | dashboard local |
| `GET /docs` | OpenAPI interactivo |
| `GET /health` | estado y versión |
| `GET /api/v1/profiles` | perfiles permitidos |
| `POST /api/v1/runs?profile=orders_v1` | valida un multipart CSV |
| `GET /api/v1/runs?limit=20&offset=0` | historial paginado |
| `GET /api/v1/runs/{id}` | resumen y primeras 100 incidencias |
| `GET /api/v1/runs/{id}/issues` | incidencias paginadas |
| `GET /api/v1/runs/{id}/issues.csv` | exportación completa segura |

Ejemplo abreviado de una respuesta `201`:

```json
{
  "id": "8f1c...",
  "filename": "8f1c....csv",
  "profile": "orders_v1",
  "status": "completed",
  "total_rows": 6,
  "valid_rows": 2,
  "invalid_rows": 4,
  "issue_count": 5,
  "created_at": "2026-10-27T18:00:00+00:00"
}
```

`filename` es un nombre técnico derivado del UUID, no el nombre original.
Errores previstos usan 413 (tamaño), 415 (extensión), 422 (estructura o
parámetros) y 503 con `Retry-After: 1` (SQLite ocupado). Un ID inexistente usa
404.

## Pruebas y evidencia

La verificación final local descubrió y aprobó **113 pruebas** sin warnings:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m compileall -q src tests scripts
node --check src\datatrust_api\static\app.js
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe scripts\smoke_http_e2e.py
```

También se comprobó un wheel `1.0.0` instalado en un entorno aislado, los
recursos empacados y un recorrido real de navegador en 360×800, 390×844,
768×1024 y 1366×768. Consulta [VERIFICACION.md](docs/VERIFICACION.md) para los
comandos y [BENCHMARK.md](docs/BENCHMARK.md) para la medición local, que no es
un SLA.

## Seguridad y privacidad

- Consultas SQL parametrizadas y transacciones con cierre explícito.
- El trabajo CPU/SQLite del POST se delega fuera del event loop.
- Límite ASGI basado en bytes recibidos; no confía solo en `Content-Length`.
- Exportación con BOM y neutralización de `=`, `+`, `-`, `@`, espacios y
  controles iniciales que una hoja de cálculo podría interpretar como fórmula.
- Cabeceras `nosniff`, `DENY`, `no-referrer` y CSP en el dashboard.
- Texto no confiable se inserta con `textContent`, no con `innerHTML`.

Estas defensas reducen riesgos de una demo local, pero no sustituyen controles
de producción. No cargues datos reales o sensibles.

## Autoría y proceso

Proyecto personal de **Yerlan Daniel Gómez Hernández**
([GitHub: yerlangomezhernandez24-afk](https://github.com/yerlangomezhernandez24-afk)).
El titular dirigió y validó el proyecto con asistencia de herramientas de IA
para revisión, pruebas y documentación. La aplicación no contiene un modelo de
IA y sus reglas se ejecutan de forma determinista y reproducible.

## Estado y roadmap

`v1.0.0` congela el producto de portafolio local. No se planean nuevas
funciones generales. Solo se atenderán defectos bloqueantes concretos. Si se
quisiera convertirlo en un servicio real, sería otro alcance: autenticación,
autorización, TLS, aislamiento, retención, observabilidad, migraciones y una
política SQLite/WAL o un motor servidor basada en mediciones.

La identidad pública, el correo GitHub `noreply` y el repositorio de destino ya
están definidos. La publicación permanece pendiente hasta crear el primer
commit y autenticar Git desde este equipo. Véanse
[DATOS_PENDIENTES_PUBLICACION.md](docs/DATOS_PENDIENTES_PUBLICACION.md) y
[CHECKLIST_PUBLICACION_GITHUB.md](docs/CHECKLIST_PUBLICACION_GITHUB.md). No se
incluye archivo `LICENSE` porque el titular aún debe elegirlo.
