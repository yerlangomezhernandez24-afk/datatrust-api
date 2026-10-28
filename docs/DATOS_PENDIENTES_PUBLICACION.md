# Datos de publicación y decisiones pendientes

Estado al 2026-10-27: el titular definió su nombre público, usuario de GitHub,
repositorio de destino y visibilidad. El proyecto todavía no tiene commits,
remoto ni licencia, y no se ha publicado.

## Identidad pública

- Nombre de autor a mostrar: `Yerlan Daniel Gómez Hernández`
- Usuario de GitHub: `yerlangomezhernandez24-afk`
- Correo público opcional: no publicado.
- Correo para commits: dirección GitHub `noreply` confirmada en los ajustes de
  la cuenta; no se documenta el correo personal.
- Perfil de LinkedIn opcional: `PENDIENTE_DEL_AUTOR`
- Repositorio de destino: `https://github.com/yerlangomezhernandez24-afk/datatrust-api`
- Visibilidad deseada: `público`
- Demo desplegada: no existe; la demostración continúa siendo local.
- Nombre público del proyecto: `DataTrust API`.

No usar el correo personal de Git si no se desea hacerlo público. GitHub permite
usar un correo `noreply`, pero la elección corresponde al titular.

## Identidad Git local

El nombre autorizado para los commits es `Yerlan Daniel Gómez Hernández` y el
correo `noreply` fue confirmado en la configuración de GitHub. La identidad se
configuró únicamente en este repositorio; para repetirlo en otra copia:

```powershell
git config --local user.name "Yerlan Daniel Gómez Hernández"
git config --local user.email "CORREO_NOREPLY_COPIADO_DE_GITHUB"
git config --get user.name
git config --get user.email
```

No se debe ejecutar el segundo comando con un valor inventado. Hay que copiarlo
desde los ajustes de GitHub y revisar el contenido preparado antes del commit.

## Licencia por elegir

No existe archivo `LICENSE`.

- **MIT:** texto corto y permisivo; permite uso, modificación y distribución
  conservando el aviso de copyright y la renuncia de garantía.
- **Apache-2.0:** también permisiva, pero más extensa; incluye una concesión
  expresa de patentes y obligaciones de avisos/cambios.

La decisión debe considerar la titularidad del código y el uso deseado. No es
asesoría legal. Tras elegir, añadir el texto oficial sin modificarlo y completar
el titular/año reales.

Metadatos locales observados en dependencias directas o relevantes:

| Paquete | Versión verificada | Expresión de licencia del paquete |
|---|---:|---|
| FastAPI | 0.162.0 | MIT |
| Starlette | 1.10.0 | BSD-3-Clause |
| Uvicorn | 0.54.0 | BSD-3-Clause |
| python-multipart | 0.0.32 | Apache-2.0 |
| Pydantic | 2.14.1 | MIT |
| pytest | 9.1.1 | MIT |
| httpx2 | 2.16.0 | BSD-3-Clause |

Estos datos provienen de la metadata instalada y deben revalidarse antes de
distribuir el proyecto; no sustituyen leer los textos de licencia oficiales.

## Revisión de privacidad

Antes de publicar, confirmar:

- [ ] No hay bases SQLite, `.env`, claves, tokens, certificados ni logs.
- [ ] No hay rutas absolutas, nombre de usuario del equipo ni datos personales.
- [ ] Solo se incluyen CSV sintéticos; `example.invalid` no representa personas.
- [ ] `.local-backups/`, `.venv*`, `build/`, `dist/`, caches y `data/` siguen
      ignorados.
- [ ] Las capturas, si se agregan luego, no muestran pestañas, correos, rutas ni
      información personal del escritorio.
- [ ] El README conserva el aviso “Not Production Ready”.
- [ ] La declaración sobre asistencia de Codex sigue visible y honesta.
