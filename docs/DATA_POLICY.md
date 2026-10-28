# Política de datos de entrada — vigente en v1.0.0

Esta política define el contrato local de los perfiles de pedidos. Busca que los límites sean explicables y reproducibles; no representa requisitos contables, fiscales ni regulatorios de una empresa real.

## Codificación y estructura CSV

- El archivo debe ser UTF-8. Se admite un único BOM UTF-8 al inicio mediante `utf-8-sig`.
- El archivo completo admite hasta 2 MiB y 10.000 filas de datos. El request multipart tiene un límite ASGI separado.
- Cada campo CSV puede ser procesado hasta el máximo físico del archivo. Después se aplican límites semánticos más pequeños por campo; así no se depende del límite implícito de 131.072 caracteres del módulo `csv`.
- Los nombres de columnas se recortan en los extremos y se normalizan a Unicode NFC solo para interpretar la estructura. Se rechazan nombres vacíos, repetidos después de normalizar, con caracteres Unicode de control/formato, mayores de 64 caracteres o mayores de 256 bytes UTF-8.
- Las columnas adicionales continúan permitidas. Un valor de columna adicional admite hasta 4.096 caracteres y 16.384 bytes UTF-8.
- Una fila vacía cuenta como fila inválida; no desaparece silenciosamente.

## Límites de los campos conocidos

Los perfiles locales declaran ambos límites y deben incluir exactamente sus campos obligatorios.

| Campo | Máximo caracteres | Máximo bytes UTF-8 |
|---|---:|---:|
| `order_id` | 128 | 256 |
| `customer_id` | 128 | 256 |
| `email` | 254 | 512 |
| `amount` | 32 | 64 |
| `currency` | 16 | 64 |
| `order_date` | 32 | 64 |

Un exceso produce la incidencia estática `VALUE_TOO_LONG`; el mensaje no contiene el valor original. Los valores se recortan en los extremos para aplicar las reglas, como ya hacía el MVP, pero no se almacenan ni se reescribe el archivo fuente.

## Identificadores y Unicode

- `order_id` y los demás campos declarados como únicos se comparan con NFC + `casefold`; el valor fuente no se modifica.
- Un identificador no puede contener categorías Unicode `Cc` (control) o `Cf` (formato), por ejemplo NUL o zero-width space. Produce `INVALID_IDENTIFIER`.
- La normalización solo establece equivalencia para validación. No translitera, elimina acentos ni modifica filas.
- Los correos mantienen una validación sintáctica deliberadamente básica y rechazan también caracteres `Cc`/`Cf`.

## Importes monetarios

- Todas las decisiones numéricas usan `Decimal`, nunca `float` binario.
- Gramática aceptada: dígitos ASCII, seguidos opcionalmente por punto y fracción. Se permiten enteros y ceros a la izquierda.
- No se aceptan signo `+`/`-`, separador de miles, coma decimal, exponente científico, `NaN` ni `Infinity`.
- No se redondea, trunca o corrige un importe inválido.
- Rango inclusivo de los perfiles actuales: `0.01` a `999999999999.99`.
- Escala máxima declarada por moneda: CRC 2, USD 2 y EUR 2 decimales en `orders_v1`; USD 2 en `orders_usd_v1`.
- Una moneda desconocida conserva su propia incidencia de enumeración. Para impedir evasión, el importe todavía se compara con la escala máxima definida por el perfil.

Los perfiles JSON expresan la política con `decimal_policies`; cada política enlaza el importe a su campo de moneda, rango, escala por moneda y prohibición explícita de notación científica.

## Errores y privacidad

- Un problema de estructura, encoding o límite global invalida el dataset y la API responde 422 sin persistencia parcial.
- Un problema de una fila produce una o más incidencias, conserva los conteos y permite revisar el resto del archivo.
- Tamaño de archivo/request responde 413; extensión real no admitida responde 415; perfil no permitido responde 422; lock agotado responde 503.
- Los errores e incidencias no incluyen nombres originales, filas, correos, identificadores ni importes recibidos.
- La exportación solo contiene incidencias estáticas y neutraliza fórmulas en cada celda de salida; no altera los datos de entrada.
