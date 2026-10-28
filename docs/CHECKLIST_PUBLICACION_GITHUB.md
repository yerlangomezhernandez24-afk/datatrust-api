# Checklist de publicación en GitHub

El titular autorizó el 27 de octubre de 2026 preparar y publicar el repositorio
`yerlangomezhernandez24-afk/datatrust-api` como público. La publicación se
completó con esa cuenta, sin sobrescribir trabajo remoto previo.

## Decisiones del titular

- [x] Definir nombre público: Yerlan Daniel Gómez Hernández.
- [x] Definir usuario: `yerlangomezhernandez24-afk`.
- [x] Definir repositorio público de destino: `datatrust-api`.
- [x] Confirmar el correo GitHub `noreply` para la identidad del commit.
- [ ] Elegir MIT, Apache-2.0 u otra licencia con criterio propio.
- [ ] Añadir el texto oficial de licencia con año y titular reales.
- [x] Confirmar `DataTrust API` como nombre público.
- [x] Definir visibilidad pública.

## Archivos permitidos

- Código bajo `src/` y pruebas bajo `tests/`.
- Scripts reproducibles bajo `scripts/`.
- `README.md`, `README.en.md`, `CHANGELOG.md`, `AGENTS.md` y `pyproject.toml`.
- Documentación técnica bajo `docs/`.
- CSV sintéticos que usen datos ficticios y dominios reservados.
- Workflow verificado remotamente y Dockerfile conservado como configuración
  inspeccionada; Docker no se declara ejecutado.

## Archivos prohibidos o que deben seguir ignorados

- `.env`, claves, tokens, certificados, contraseñas o credenciales.
- `.venv/`, `.venv-*`, caches, `*.pyc` y `*.egg-info`.
- Bases `*.sqlite*`, `*.db*`, journals, `data/` y backups.
- `.local-backups/`, `build/`, `dist/`, wheels y ZIP de trabajo.
- Logs, cobertura local, archivos temporales y capturas con información privada.
- Datos personales, empresariales o datasets sin licencia.

## Auditoría previa

```powershell
git status --short --ignored
git diff --check
git remote -v
git config --get user.name
git config --get user.email
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe scripts\check_version.py --installed
.\.venv\Scripts\python.exe -m pip check
```

- [x] Revisar manualmente cada archivo no ignorado.
- [x] Buscar rutas absolutas y nombres de usuario locales.
- [x] Buscar patrones de secretos; un resultado vacío reduce riesgo, no lo elimina.
- [x] Confirmar que los únicos CSV publicados son sintéticos.
- [x] Confirmar que README dice “Not Production Ready”.
- [x] Confirmar coherencia `1.0.0` en código, metadata y `/health`.
- [ ] Revalidar licencias de dependencias desde fuentes oficiales antes de
  distribuir binarios.

## Git y publicación

Estado final: rama local `main` vinculada a `origin/main`. El nombre y el
correo `noreply` están configurados solo para este repositorio. Se publicaron:

1. `84b7b1b3c59160a5cb870f402766498fa20bf7ec`: referencia v1.0.0;
2. `cffa751028bc625f29f4cc80c2575116ff97afda`: actualización de Actions.

Repositorio:
`https://github.com/yerlangomezhernandez24-afk/datatrust-api`.

- [x] Remoto añadido conscientemente y rama `main` publicada.
- [x] Autoría conservada como Yerlan Daniel Gómez Hernández.
- [x] Topics guardados: `python`, `fastapi`, `data-quality`, `sqlite`,
      `csv`, `rest-api`, `pytest`, `portfolio-project`, `automation`.
- [x] README, código y documentación visibles en GitHub.

No incluir comandos con credenciales ni tokens en documentación o historial.

## CI y Docker

- [x] Ejecutar GitHub Actions en Python 3.11 y 3.12 y conservar el
      [resultado verde](https://github.com/yerlangomezhernandez24-afk/datatrust-api/actions/runs/40632875253).
- [ ] Probar `Dockerfile` con Docker disponible y publicar solo en
  `127.0.0.1:8000` para la demo.
- [x] Documentar el resultado real sin inventar un badge.
- [x] No desplegar a Internet sin abrir un nuevo alcance de seguridad.
