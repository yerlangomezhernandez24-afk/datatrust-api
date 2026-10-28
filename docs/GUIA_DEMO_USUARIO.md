# Guía de demo para usuarios

Esta guía explica DataTrust API sin requerir conocimientos de programación. Es
una demostración local con datos inventados, no un sistema empresarial.

## Antes de empezar

Pide a la persona técnica que instale el proyecto siguiendo el README y que
ejecute:

```powershell
.\scripts\iniciar_demo.ps1
```

La pantalla debe estar disponible en `http://127.0.0.1:8000/` y mostrar
**API local activa · v1.0.0**. Si el script no puede ejecutarse, el README
incluye el comando directo equivalente.

## Recorrido de seis pedidos

1. Pulsa **Demo de 6 pedidos** para descargar el archivo sintético.
2. En **Perfil de reglas**, conserva `orders_v1`.
3. En **Archivo CSV**, selecciona `demo-orders-6.csv`.
4. Pulsa **Validar archivo**.
5. Debes ver: 6 filas totales, 2 válidas, 4 inválidas y 5 incidencias.
6. En **Incidencias**, revisa las filas 3 a 6. La fila 6 tiene dos problemas,
   por eso hay 4 filas inválidas pero 5 incidencias.
7. Pulsa **Exportar CSV seguro** para descargar el diagnóstico.

Los códigos esperados son `DUPLICATE`, `INVALID_EMAIL`, `INVALID_AMOUNT`,
`INVALID_CURRENCY` e `INVALID_DATE`.

## Recorrido de cien pedidos

Repite el proceso con **Demo de 100 pedidos**. El resultado esperado es:

- 100 filas totales;
- 90 válidas;
- 10 inválidas;
- 10 incidencias `INVALID_EMAIL`.

Las filas problemáticas son las diez últimas. El objetivo es mostrar que el
sistema ofrece el mismo resultado cada vez con la misma entrada.

## Qué significa cada área

- **Perfil de reglas:** conjunto local y versionado de condiciones. El perfil
  USD rechaza monedas que no sean USD.
- **Total de filas:** registros de datos; el encabezado no cuenta.
- **Válidas:** filas sin ninguna incidencia.
- **Inválidas:** filas con al menos una incidencia.
- **Incidencias:** problemas individuales; una fila puede sumar varios.
- **Fila:** posición en el CSV contando el encabezado como fila 1.
- **Campo:** columna relacionada con el problema; `_row` indica estructura.
- **Código:** identificador estable que una automatización puede interpretar.
- **Mensaje:** explicación breve para una persona.
- **Historial:** resúmenes guardados en la base local. Los nombres visibles son
  UUID técnicos; el nombre original no se almacena.

En pantallas pequeñas, la tabla se desliza horizontalmente para enseñar todas
las columnas. Los controles mantienen un alto táctil mínimo de 44 píxeles.

## Probar un error controlado

Selecciona `examples/orders_invalid_structure.csv` y pulsa **Validar archivo**.
Debe aparecer un aviso rojo que empieza por **Faltan columnas obligatorias**.
No se crea una ejecución nueva. Otros mensajes posibles son:

- 413: archivo o solicitud demasiado grande;
- 415: extensión distinta de `.csv`;
- 422: estructura, codificación o parámetro inválido;
- 503: SQLite estuvo ocupado; espera y reintenta.

## Privacidad y alcance

Usa solo los archivos sintéticos incluidos. El selector del navegador muestra
temporalmente el nombre del archivo que la propia persona eligió; el servidor
no lo conserva ni lo devuelve. Tampoco almacena el contenido original de las
filas. Sí guarda:

- UUID de ejecución y nombre neutral derivado;
- perfil, estado, fecha y conteos;
- número de fila, campo, código y mensaje estático de cada incidencia.

No hay login, permisos, TLS, cifrado en reposo ni separación de usuarios. Por
eso no debe exponerse a Internet ni recibir información real o confidencial.

## Utilidad hipotética para una empresa

La demo ilustra un control previo a una importación: detectar errores antes de
que lleguen a un ERP o reporte. Una adopción real requeriría validar reglas con
usuarios, medir volúmenes, definir responsabilidades, retención, seguridad y
conectores. Este proyecto demuestra la ingeniería del flujo; no afirma que una
empresa lo utilice.

## Cerrar la demo

Vuelve a la ventana de PowerShell donde corre el servidor y presiona `Ctrl+C`.
No cierres el proceso interrumpiendo archivos de una base personal; la
configuración predeterminada usa `data/datatrust.sqlite3` dentro del proyecto.

La interfaz fue verificada con navegador real en 360×800, 390×844, 768×1024 y
1366×768. Las capturas se observaron durante la ejecución de Codex, pero no se
guardaron en el repositorio para evitar incluir artefactos dependientes del
equipo del autor.
