# Caso de estudio de portafolio — DataTrust API

## Resumen

DataTrust API es un proyecto personal asistido por Codex que demuestra diseño
de API, validación de datos, persistencia SQLite, seguridad defensiva y QA
automatizado. La release `1.0.0` es una demo local reproducible, no experiencia
laboral remunerada ni un producto desplegado.

## Problema

Los errores de un CSV suelen descubrirse durante una importación, cuando ya
cuestan tiempo de diagnóstico. La hipótesis del proyecto fue: **si las reglas
son explícitas y el resultado señala fila, campo y código, una persona puede
corregir el archivo antes de integrarlo**.

Usuarios hipotéticos:

- analista que prepara un lote de pedidos;
- desarrollador que integra un sistema interno;
- responsable de QA que necesita casos reproducibles;
- estudiante que quiere comprender una API y sus fallos controlados.

No se entrevistaron usuarios reales ni se midió impacto empresarial. La
hipótesis sigue pendiente de validación externa.

## Decisiones técnicas

1. **Reglas deterministas, no IA.** Correos, importes, monedas y fechas se
   validan con código auditable. Un modelo no mejoraría este cálculo exacto.
2. **FastAPI + separación por capas.** `main.py` traduce HTTP, `validator.py`
   valida, `profiles.py` carga configuración permitida y `store.py` persiste.
3. **SQLite local.** Reduce fricción para una demo de un usuario y un worker.
   No se presenta como solución multiusuario.
4. **Minimización de datos.** La base guarda resúmenes e incidencias estáticas,
   no filas ni nombres originales.
5. **Perfiles JSON permitidos.** Dos perfiles locales versionados demuestran
   extensibilidad sin aceptar rutas o reglas arbitrarias.
6. **Exportación segura.** Los prefijos de fórmula se neutralizan al exportar,
   sin alterar indiscriminadamente los datos recibidos.

## Arquitectura

```text
CSV sintético → límite ASGI → parser multipart → validador + perfil
                                             ├→ respuesta resumen
                                             └→ transacción SQLite
Navegador ← API REST ← historial/incidencias ← consultas parametrizadas
                     └→ exportación CSV por streaming
```

El endpoint de carga es `async`, pero el trabajo síncrono de validación y
SQLite se ejecuta en el thread pool. Las conexiones se cierran incluso ante
excepciones y las escrituras usan una transacción completa.

## Errores encontrados durante la construcción

La estabilización no se limitó al camino feliz. Las regresiones reprodujeron y
corrigieron, entre otros, estos problemas:

- validar extensiones después de manipular nombres largos;
- offsets fuera del rango entero de SQLite que provocaban HTTP 500;
- conexiones que podían quedar abiertas ante errores;
- configuración `:memory:` incompatible con conexiones independientes;
- persistencia y exposición del nombre original potencialmente sensible;
- trabajo bloqueante ejecutado dentro del event loop;
- confiar solo en `Content-Length` para limitar un multipart;
- fórmulas peligrosas al abrir exportaciones en hojas de cálculo;
- locks de lectura/escritura traducidos de forma inconsistente;
- diferencias entre recursos fuente y activos incluidos en el wheel.

Cada corrección relevante quedó acompañada por una prueba. No se eliminaron
casos para obtener una suite verde.

## Estrategia de pruebas

Las 113 pruebas finales cubren:

- funciones puras de validación y perfiles JSON;
- API mediante cliente ASGI;
- límites exactos de 2 MiB y 10.000/10.001 filas;
- UTF-8, BOM, Unicode normalizado, controles invisibles y CSV mal formado;
- privacidad, nombres sensibles y ausencia de filas originales en SQLite;
- paginación real y límites enteros;
- concurrencia coordinada, timeout, rollback y 503 con `Retry-After`;
- backup/restauración en bases sintéticas;
- exportación completa y neutralización de fórmulas;
- smoke HTTP con Uvicorn real y base temporal;
- recursos de los escenarios de 6 y 100 pedidos.

Además, se instaló desde fuente y desde wheel en entornos virtuales separados,
se inspeccionaron los recursos empacados y se recorrió la interfaz con un
navegador real en cuatro tamaños.

## Métricas: demo frente a realidad

Métricas verificadas de los archivos sintéticos:

| Caso | Total | Válidas | Inválidas | Incidencias |
|---|---:|---:|---:|---:|
| Demo 6 | 6 | 2 | 4 | 5 |
| Demo 100 | 100 | 90 | 10 | 10 |

El benchmark local del 2026-10-27 midió una mediana de 177,815 ms para validar
10.000 filas en Python 3.12.14 sobre el equipo de prueba. Es una medición del
validador puro, secuencial y con datos sintéticos; no representa latencia HTTP,
usuarios concurrentes, un SLA ni ahorro económico.

## Límites y riesgos

- No hay autenticación, autorización, TLS, auditoría de usuarios ni cifrado.
- SQLite usa journal predeterminado y un worker. WAL mostró ventajas en un
  experimento lector/escritor, pero no se activó sin una política operativa.
- No existe migración de esquema, retención, borrado ni recuperación empresarial.
- La validación de email es deliberadamente simple, no RFC completa.
- MIME y extensión no prueban la naturaleza del contenido.
- No se ejecutaron Python 3.11, Docker ni GitHub Actions en este equipo.

## Transparencia sobre IA

Codex ayudó a inspeccionar, proponer pruebas, editar código/documentación y
ejecutar verificaciones. Las reglas y resultados son deterministas y se pueden
reproducir localmente. El proyecto no contiene un modelo de IA ni atribuye a la
IA decisiones de negocio. La autoría pública corresponde a Yerlan Daniel Gómez
Hernández; la elección de licencia continúa pendiente del titular.

## Conclusión

La hipótesis técnica quedó demostrada para un entorno local: una persona puede
instalar, cargar datos sintéticos, interpretar resultados y exportar
incidencias. El proyecto se congela como pieza de portafolio. Convertirlo en un
servicio real sería un nuevo producto y requeriría primero investigación con
usuarios y controles de seguridad completos.
