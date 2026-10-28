# Demo para reclutadores — guion de 2 a 3 minutos

## Preparación

1. Iniciar en `127.0.0.1` con un worker.
2. Abrir `http://127.0.0.1:8000/`.
3. Tener disponibles los enlaces **Demo de 6 pedidos** y **Demo de 100 pedidos**.
4. No usar datos personales ni afirmar que es producción.

## Guion

**0:00–0:25 — problema.**

> DataTrust API es un proyecto personal de calidad de datos. Detecta errores de
> pedidos antes de una importación y explica fila, campo, código y mensaje. No
> usa IA porque las reglas son deterministas.

**0:25–1:05 — flujo visible.**

Descargar la demo de 6 pedidos, conservar `orders_v1`, cargarla y validar.
Señalar 6 totales, 2 válidas, 4 inválidas y 5 incidencias. Explicar que una fila
puede tener más de un problema. Abrir la lista y mostrar `DUPLICATE`,
`INVALID_EMAIL`, `INVALID_AMOUNT`, `INVALID_CURRENCY` e `INVALID_DATE`.

**1:05–1:30 — exportación y privacidad.**

Pulsar **Exportar CSV seguro**. Explicar que la exportación neutraliza prefijos
de fórmula y que SQLite solo guarda resumen e incidencias. El nombre visible de
la ejecución es un UUID neutral; las filas y el nombre original no se guardan.

**1:30–2:00 — escala comprobada.**

Cargar la demo de 100 pedidos: 90 válidas, 10 inválidas y 10 incidencias.
Mencionar límites honestos: 2 MiB, 10.000 filas, un usuario y un worker.

**2:00–2:35 — ingeniería.**

Abrir `/docs`. Mencionar 113 pruebas, límite ASGI por bytes reales, consultas
parametrizadas, transacciones, locks SQLite convertidos en 503, instalación
limpia, wheel verificado y E2E real en cuatro viewports.

**2:35–3:00 — cierre.**

> La versión 1.0.0 es una Portfolio Local Release, no un servicio público. Para
> producción harían falta autenticación, autorización, TLS, aislamiento,
> retención, observabilidad y una estrategia de base de datos medida.

## Preguntas técnicas frecuentes

### ¿Por qué SQLite?

Porque permite una instalación local reproducible y transacciones reales sin
infraestructura. Se limita explícitamente a un worker. Un experimento mostró
que WAL favorece lector/escritor, pero no se activó sin una política operativa.

### ¿Por qué no usaste IA?

Las reglas de formato, rango y unicidad son exactas y auditables. Añadir un
modelo aumentaría costo y opacidad sin demostrar valor. La asistencia de Codex
se declara como herramienta de desarrollo, no como función del producto.

### ¿Cómo proteges información sensible?

El diseño no persiste filas originales ni filenames. Los mensajes son
estáticos, SQL usa parámetros, el dashboard usa `textContent`, el request tiene
límite ASGI y la exportación neutraliza fórmulas. Aun así, no existe seguridad
multiusuario y solo se deben usar datos sintéticos.

### ¿Qué diferencia hay entre fila inválida e incidencia?

Una fila inválida es un registro con uno o más problemas. Cada problema es una
incidencia. En la demo de 6, una fila tiene moneda y fecha inválidas; por eso 4
filas inválidas producen 5 incidencias.

### ¿Qué probaste realmente?

Python 3.12.14 en Windows 11: 113 pruebas sin warnings, `compileall`, JavaScript,
`pip check`, Uvicorn real, wheel instalado aparte, backup/restauración,
concurrencia coordinada y navegador 360/390/768/1366. Python 3.11, Docker y CI
remota no estaban disponibles y no se marcan como aprobados.

### ¿Cuál fue un defecto interesante?

Confiar en `Content-Length` no basta: puede faltar o ser falso. El middleware
cuenta los bytes ASGI recibidos antes de que Starlette procese todo el multipart
y conserva un límite separado para el archivo CSV.

### ¿Qué harías después?

No añadiría funciones por inercia. Si hubiera interés real, validaría primero
el flujo con usuarios y mediría volumen/concurrencia. Solo entonces diseñaría
autenticación, retención, observabilidad y almacenamiento.

## Frase breve y honesta

> Proyecto personal asistido por Codex: diseñé y verifiqué una API local de
> calidad de datos con FastAPI y SQLite, validación reproducible, privacidad por
> minimización, exportación segura y 113 pruebas. No está desplegada ni se
> presenta como experiencia laboral o servicio de producción.
