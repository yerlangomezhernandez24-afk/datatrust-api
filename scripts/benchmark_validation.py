"""Benchmark local reproducible del validador puro con datos sintéticos."""

from __future__ import annotations

import argparse
import json
import os
import platform
import statistics
import sys
from time import perf_counter

from datatrust_api.validator import validate_orders_csv

HEADER = b"order_id,customer_id,email,amount,currency,order_date\n"


def synthetic_csv(row_count: int) -> bytes:
    rows = (
        f"B-{index},C-{index},user{index}@example.invalid,19.99,USD,2026-10-25\n".encode()
        for index in range(row_count)
    )
    return HEADER + b"".join(rows)


def benchmark(row_count: int, repeats: int) -> dict:
    payload = synthetic_csv(row_count)
    expected = (row_count, row_count, [])
    if validate_orders_csv(payload) != expected:
        raise RuntimeError("El dataset sintético no produjo el resultado esperado.")

    samples_ms = []
    for _ in range(repeats):
        started = perf_counter()
        result = validate_orders_csv(payload)
        elapsed_ms = (perf_counter() - started) * 1000
        if result != expected:
            raise RuntimeError("El validador cambió de resultado durante el benchmark.")
        samples_ms.append(elapsed_ms)

    median_ms = statistics.median(samples_ms)
    return {
        "rows": row_count,
        "payload_bytes": len(payload),
        "repeats": repeats,
        "min_ms": round(min(samples_ms), 3),
        "median_ms": round(median_ms, 3),
        "max_ms": round(max(samples_ms), 3),
        "rows_per_second_median": round(row_count / (median_ms / 1000), 1),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", nargs="+", type=int, default=[100, 1_000, 10_000])
    parser.add_argument("--repeats", type=int, default=5)
    args = parser.parse_args()
    if args.repeats < 1 or any(rows < 1 or rows > 10_000 for rows in args.rows):
        parser.error("rows debe estar entre 1 y 10000 y repeats debe ser positivo")

    report = {
        "method": "validate_orders_csv; una preparación no medida y repeticiones secuenciales",
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "processor": platform.processor() or "no informado por platform.processor()",
        "logical_cpus": os.cpu_count(),
        "results": [benchmark(rows, args.repeats) for rows in args.rows],
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
