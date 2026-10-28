# Informe de publicación en GitHub

**Proyecto:** DataTrust API v1.0.0

**Fecha:** 27 de octubre de 2026

**Estado:** PUBLICADO Y VERIFICADO

**Autor:** Yerlan Daniel Gómez Hernández

**Repositorio:** <https://github.com/yerlangomezhernandez24-afk/datatrust-api>

## Resultado

DataTrust API quedó publicado como repositorio público en la rama `main`. El
código, las pruebas, el README en español e inglés y la documentación técnica
son visibles. No se desplegó la aplicación, no se habilitó GitHub Pages y no se
publicaron paquetes: el producto sigue siendo una demo local y no se declara
apto para producción.

## Historial publicado

| Commit | Propósito |
|---|---|
| `84b7b1b3c59160a5cb870f402766498fa20bf7ec` | Referencia de portafolio DataTrust API v1.0.0 |
| `cffa751028bc625f29f4cc80c2575116ff97afda` | Actualización de runtimes de GitHub Actions |

El nombre de autor se conservó como Yerlan Daniel Gómez Hernández y el correo
del commit usa la dirección `noreply` confirmada por el titular en GitHub. No
se reescribió el historial para simular fechas o commits antiguos.

## Verificaciones ejecutadas

### Entorno local

- Python 3.12.14 y pip 25.0.1.
- Versión coherente `1.0.0` en fuente, `pyproject.toml`, FastAPI y metadata
  instalada.
- `pip check`, `compileall` y `node --check`: código de salida 0.
- Smoke HTTP real: health, dashboard, perfiles, listados, detalle, paginación y
  exportación respondieron 200; la carga válida respondió 201; un ID
  inexistente respondió 404; el exceso de tamaño respondió 413 sin persistir;
  el CSV exportado incluyó BOM y las cabeceras defensivas estuvieron presentes.
- Suite antes de publicar: **113 passed in 7.33s**.
- Suite después de actualizar el workflow: **113 passed in 8.79s**.
- Verificación documental final: **113 passed in 7.31s**.

### GitHub Actions

La primera ejecución completó sus dos jobs en 23 s, pero mostró advertencias de
runtimes Node obsoletos en las versiones usadas por las acciones. Se
actualizaron `actions/checkout` y `actions/setup-python` a v7.

La segunda ejecución terminó correctamente:

- URL:
  <https://github.com/yerlangomezhernandez24-afk/datatrust-api/actions/runs/40632875253>
- Python 3.11: aprobado.
- Python 3.12: aprobado.
- Duración total mostrada por GitHub: 27 s.
- Advertencias de runtimes Node: 0.
- Avisos informativos: 2, relacionados con la migración futura de
  `ubuntu-latest`; no fueron fallos ni advertencias del proyecto.

## Auditoría de publicación

Antes del primer commit se revisaron los 88 archivos publicables. No se
encontraron rutas prohibidas, enlaces Markdown locales rotos, enlaces
simbólicos, archivos mayores de 1 MiB ni patrones evidentes de secretos.

Se confirmó que no entraron en Git:

- entornos `.venv*` ni metadata editable generada;
- bases SQLite, journals, `data/` ni datos reales;
- `.env`, claves, tokens, certificados o credenciales;
- caches, `*.pyc`, logs o archivos temporales;
- `.local-backups/`, ZIP, wheels, `build/` o `dist/`;
- `node_modules/` ni configuración privada de IDE.

Los CSV versionados son demostraciones sintéticas y usan dominios reservados.
El proyecto no conserva nombres originales de archivos ni filas originales en
SQLite.

Se creó un respaldo local previo a la publicación:

- archivo:
  `.local-backups/datatrust-v1.0.0-pre-github-20261027-221617.zip`;
- SHA-256:
  `5FA654F2C8F45DFB97E796093BA7D84CC77D6A7C486423BE663941279315EA66`;
- 88 entradas y 0 entradas prohibidas.

El respaldo está ignorado y no fue publicado.

## Metadatos del repositorio

La descripción pública resume el alcance local de calidad de datos. Se
guardaron los temas:

`python`, `fastapi`, `data-quality`, `sqlite`, `csv`, `rest-api`,
`pytest`, `portfolio-project` y `automation`.

No se creó una release binaria, un paquete ni una demo alojada.

## Incidencias y decisiones

- La resolución DNS del equipo no pudo resolver temporalmente
  `github.com`/API. Para la autenticación y los pushes se utilizó un túnel
  local efímero restringido a esos hosts, con TLS de extremo a extremo. Se
  cerró después de usarlo y no se cambió la configuración DNS del sistema.
- El acceso OAuth fue el flujo oficial de Git Credential Manager autorizado por
  el titular. No se copiaron contraseñas, PAT ni códigos 2FA al repositorio.
- No existe archivo `LICENSE`: elegir MIT, Apache-2.0 u otra opción sigue
  siendo una decisión del titular y no debe inventarse.
- Docker no está disponible en este equipo; el Dockerfile fue inspeccionado,
  pero no se afirma que haya sido ejecutado.
- La ejecución manual en macOS/Linux y un pentest externo siguen pendientes.

## Explicación didáctica

- Un **repositorio** es el proyecto y su historial completo.
- Un **commit** es una fotografía identificada por un hash; permite saber
  exactamente qué contenido se revisó.
- Una **rama**, en este caso `main`, es la línea principal de esas fotografías.
- Un **remoto**, aquí `origin`, enlaza la copia local con GitHub.
- Un **push** envía commits ya creados; no vuelve segura una aplicación ni la
  despliega automáticamente.
- **GitHub Actions** crea entornos limpios y ejecuta el workflow. Que CI esté
  verde demuestra que los comandos configurados pasaron en esos entornos; no
  demuestra seguridad de producción.

Para una actualización futura: modificar solo lo necesario, ejecutar la suite,
revisar `git diff`, comprobar que no se agregaron secretos, crear un commit
descriptivo y hacer push. Si cambia el contrato o la seguridad, también se debe
actualizar la documentación y volver a revisar el alcance local.
