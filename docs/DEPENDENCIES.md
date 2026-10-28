# Estrategia de dependencias y reproducibilidad

## Dos niveles deliberados

1. `pyproject.toml` declara rangos compatibles para instalaciones normales y Python 3.11+.
2. `constraints/verified-py312.txt` reproduce las versiones observadas con Python 3.12.14 el 27 de octubre de 2026.

El constraints es un snapshot probado, no un lock universal de sistemas operativos ni evidencia para Python 3.11.

## Dependencias de desarrollo

- pytest `>=8,<10`.
- `httpx2>=2,<3`, la interfaz que Starlette 1.10 prioriza para `TestClient`.

La migración se validó en una venv descartable y en la venv de trabajo con `httpx2 2.16.0`, `httpcore2 2.16.0` y `truststore 0.10.5`. La suite dejó de emitir el warning del fallback a HTTPX 0.28.1. No se ocultan warnings mediante filtros.

Referencias oficiales usadas para comprobar la transición: <https://pypi.org/project/httpx2/> y <https://github.com/Kludex/starlette/blob/main/starlette/testclient.py>.

## Instalación reproducible Python 3.12

```powershell
python -m pip install -c constraints/verified-py312.txt -e ".[dev]"
python scripts/check_version.py --installed
python -m pip check
python -m compileall -q src tests scripts
python -m pytest -q -p no:cacheprovider
python scripts/smoke_http_e2e.py
```

En esta ejecución se instalaron herramientas de construcción dentro de entornos virtuales locales, nunca en el Python global. Fuente, paquete instalado, FastAPI y `pyproject.toml` quedaron coherentes.

En el cierre v1.0.0 se repitió el procedimiento en `.venv-v1-source-py312` y se instaló el wheel final en `.venv-v1-wheel-py312`. Ambos reportaron versión 1.0.0 y `pip check` correcto. El wheel final incluyó los perfiles y todos los activos de dashboard/demos. Los directorios son artefactos locales ignorados, no contenido de la release.

## Procedimiento de actualización

1. Crear una venv limpia por cada Python soportado.
2. Instalar desde rangos sin modificar el entorno global.
3. Ejecutar versión instalada, `pip check`, compilación, suite y smoke HTTP.
4. Revisar warnings y changelogs de dependencias directas.
5. Actualizar el snapshot solo con versiones realmente ejecutadas.
6. Conservar como pendiente cualquier plataforma o intérprete no disponible.

No se agregaron Ruff, Black, mypy, Playwright como paquete ni bibliotecas ML. Para este alcance, `compileall`, pruebas y `node --check` aportaron valor sin ampliar innecesariamente el stack; no se presentan como sustituto de lint o análisis de tipos.
