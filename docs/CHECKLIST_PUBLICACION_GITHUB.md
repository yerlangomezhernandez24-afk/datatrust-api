# Checklist de publicación en GitHub

El titular autorizó el 27 de octubre de 2026 preparar y publicar el repositorio
`yerlangomezhernandez24-afk/datatrust-api` como público. La ejecución sigue
condicionada a autenticar Git exactamente con esa cuenta y comprobar que el
destino no contiene trabajo que pueda sobrescribirse.

## Decisiones del titular

- [x] Definir nombre público: Yerlan Daniel Gómez Hernández.
- [x] Definir usuario: `yerlangomezhernandez24-afk`.
- [x] Definir repositorio público de destino: `datatrust-api`.
- [x] Confirmar el correo GitHub `noreply` para la identidad del commit.
- [ ] Elegir MIT, Apache-2.0 u otra licencia con criterio propio.
- [ ] Añadir el texto oficial de licencia con año y titular reales.
- [ ] Revisar si `DataTrust API` seguirá siendo el nombre público.
- [ ] Definir visibilidad del futuro repositorio.

## Archivos permitidos

- Código bajo `src/` y pruebas bajo `tests/`.
- Scripts reproducibles bajo `scripts/`.
- `README.md`, `README.en.md`, `CHANGELOG.md`, `AGENTS.md` y `pyproject.toml`.
- Documentación técnica bajo `docs/`.
- CSV sintéticos que usen datos ficticios y dominios reservados.
- Workflow y Dockerfile como configuración inspeccionada, sin afirmar que CI o
  Docker se ejecutaron si no hay evidencia.

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

- [ ] Revisar manualmente cada archivo no ignorado.
- [ ] Buscar rutas absolutas y nombres de usuario locales.
- [ ] Buscar patrones de secretos; un resultado vacío reduce riesgo, no lo elimina.
- [ ] Confirmar que los únicos CSV publicados son sintéticos.
- [ ] Confirmar que README dice “Not Production Ready”.
- [ ] Confirmar coherencia `1.0.0` en código, metadata y `/health`.
- [ ] Revalidar licencias de dependencias desde fuentes oficiales antes de
  distribuir binarios.

## Git pendiente

Estado de preparación: rama local `main`, sin commits ni remoto. El nombre y el
correo `noreply` están configurados solo para este repositorio; la autenticación
de Git sigue pendiente. Antes de publicar se debe:

1. autenticar Git con la cuenta `yerlangomezhernandez24-afk`;
2. revisar y preparar el primer commit;
3. crear el repositorio remoto en su propia cuenta;
4. añadir el remoto conscientemente;
5. ejecutar CI y revisar el resultado real;
6. publicar solo después de una última revisión de privacidad.

Topics previstos: `python`, `fastapi`, `data-quality`, `sqlite`, `csv`,
`rest-api`, `pytest`, `portfolio-project`, `automation`.

No incluir comandos con credenciales ni tokens en documentación o historial.

## CI y Docker

- [ ] Ejecutar GitHub Actions en Python 3.11 y 3.12 y conservar el resultado.
- [ ] Probar `Dockerfile` con Docker disponible y publicar solo en
  `127.0.0.1:8000` para la demo.
- [ ] No convertir un CI remoto pendiente en un “badge verde” inventado.
- [ ] No desplegar a Internet sin abrir un nuevo alcance de seguridad.
