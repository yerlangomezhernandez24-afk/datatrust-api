# Benchmark T-104 — validador puro

## Revalidación v1.0.0 — 27 de octubre de 2026

Comando: `python scripts/benchmark_validation.py --rows 100 1000 10000 --repeats 5`.

| Filas | Bytes CSV | Mínimo | Mediana | Máximo | Filas/s sobre mediana |
|---:|---:|---:|---:|---:|---:|
| 100 | 5.424 | 1,602 ms | 1,697 ms | 2,363 ms | 58.931,0 |
| 1.000 | 56.724 | 16,091 ms | 16,832 ms | 18,496 ms | 59.410,3 |
| 10.000 | 596.724 | 175,363 ms | 177,815 ms | 188,405 ms | 56.238,3 |

Entorno: Windows 11 `10.0.26200`, Python 3.12.14, procesador `Intel64 Family 6 Model 142 Stepping 12, GenuineIntel` y 8 CPU lógicas. La metodología no cambió respecto de v0.3.0. Esta variación local no prueba una mejora o regresión causal y no es un SLA.

## Revalidación v0.3.0 — 27 de octubre de 2026

Se repitió el mismo comando dos veces tras el cierre de calidad. La segunda ejecución completa produjo:

| Filas | Bytes CSV | Mínimo | Mediana | Máximo | Filas/s sobre mediana |
|---:|---:|---:|---:|---:|---:|
| 100 | 5.424 | 1,615 ms | 1,815 ms | 2,533 ms | 55.087,3 |
| 1.000 | 56.724 | 16,209 ms | 17,735 ms | 17,871 ms | 56.386,6 |
| 10.000 | 596.724 | 175,779 ms | 185,589 ms | 186,475 ms | 53.882,5 |

El entorno continuó siendo Windows 11 `10.0.26200`, Python 3.12.14, el mismo procesador informado y 8 CPU lógicas. La primera repetición del cierre tuvo mediana 1,804/19,691/188,822 ms. Ambas son más lentas que la medición histórica inferior, pero una ejecución local sin control de carga, energía o antivirus no permite atribuir causalidad a una regresión. Se conservan ambos registros y no se promete throughput.

Fecha: 25 de octubre de 2026.

## Entorno medido

- Windows 11 `10.0.26200`
- Python 3.12.14
- Procesador informado: `Intel64 Family 6 Model 142 Stepping 12, GenuineIntel`
- 8 CPU lógicas
- Datos CSV 100% sintéticos y válidos, perfil `orders_v1`

## Metodología

Comando ejecutado:

```powershell
.\.venv\Scripts\python.exe scripts\benchmark_validation.py --rows 100 1000 10000 --repeats 5
```

Para cada tamaño se construyó el payload una vez, se hizo una preparación no medida y luego cinco validaciones secuenciales con `perf_counter`. Se verificó en cada repetición que todas las filas siguieran siendo válidas. La tabla informa mínimo, mediana y máximo; no se descartaron muestras.

| Filas | Bytes CSV | Mínimo | Mediana | Máximo | Filas/s sobre mediana |
|---:|---:|---:|---:|---:|---:|
| 100 | 5.424 | 0,862 ms | 0,875 ms | 0,890 ms | 114.311,8 |
| 1.000 | 56.724 | 8,098 ms | 9,163 ms | 9,934 ms | 109.128,6 |
| 10.000 | 596.724 | 85,402 ms | 87,787 ms | 92,872 ms | 113.912,0 |

## Interpretación correcta

Estos números miden solo `validate_orders_csv` en este equipo y momento. No incluyen HTTP, multipart, escritura SQLite, antivirus, red ni usuarios concurrentes. No son un SLA, una comparación comercial ni evidencia de rendimiento en producción. El script permite repetir la medición en otro equipo sin reutilizar estos valores como si fueran universales.
