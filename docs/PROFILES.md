# Perfiles JSON locales

Estado: subconjunto seguro ampliado en v0.2.1 y vigente sin cambio de contrato en v1.0.0.

Los perfiles se incluyen dentro del paquete en `src/datatrust_api/profile_data/` y solo pueden seleccionarse por un identificador del registro interno. La API no acepta rutas, JSON subido por usuarios ni código ejecutable.

## Perfiles disponibles

- `orders_v1`: columnas de pedidos y monedas CRC, USD o EUR.
- `orders_usd_v1`: mismas columnas y reglas, pero solo permite USD.

Usar el query parameter `profile` al cargar:

```powershell
curl.exe -X POST "http://127.0.0.1:8000/api/v1/runs?profile=orders_usd_v1" `
  -F "file=@examples/orders_valid.csv;type=text/csv"
```

`GET /api/v1/profiles` devuelve id, versión y descripción para que clientes y dashboard no tengan que conocer la lista de antemano.

## Esquema permitido

Cada JSON contiene exactamente estas claves:

| Clave | Regla |
|---|---|
| `id` | Identificador local que termina en `_vN` y coincide con el registro. |
| `version` | Entero positivo coherente con el sufijo del id. |
| `description` | Texto de 1 a 200 caracteres. |
| `max_rows` | Entero entre 1 y 10.000. |
| `required_fields` | Lista no vacía de nombres de columna únicos. |
| `identifier_fields` | Identificadores que rechazan caracteres Unicode de control/formato. |
| `unique_fields` | Campos cuya repetición se detecta con NFC + `casefold`. |
| `email_fields` | Campos validados con el patrón básico de email. |
| `positive_decimal_fields` | Campos que deben tener una política decimal explícita. |
| `field_limits` | Máximo de caracteres y bytes UTF-8 para cada campo requerido. |
| `decimal_policies` | Rango, campo de moneda, escala por moneda y prohibición de notación científica. |
| `enum_fields` | Mapa de campo a lista local de valores permitidos. |
| `iso_date_fields` | Campos de fecha ISO real `AAAA-MM-DD`. |

Se rechazan claves JSON duplicadas, claves desconocidas, reglas sobre campos no requeridos, listas duplicadas/vacías inválidas y tipos incorrectos. No existe `eval`, regex aportada por clientes, import dinámico ni operador de script.

## Cómo añadir uno de forma controlada

1. Crear un JSON local que cumpla el esquema.
2. Añadir su id y nombre de archivo a `PROFILE_FILES` en `profiles.py`.
3. Añadir pruebas de reglas, error y compatibilidad.
4. Actualizar esta documentación y el changelog.

Esto es deliberadamente un subconjunto, no una promesa de validación genérica universal.

El contrato concreto de importes, Unicode, encabezados y columnas adicionales está en [DATA_POLICY.md](DATA_POLICY.md).
