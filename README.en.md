# DataTrust API · v1.0.0

**Portfolio Local Release — Not Production Ready**

DataTrust API is a personal, educational Software Engineering and Automation
project. It validates order CSV files with deterministic rules, explains each
problem, and exports a safe issue report. It runs locally with synthetic data;
it does not use AI, paid services, or third-party APIs.

[Spanish README](README.md) · [User guide](docs/GUIA_DEMO_USUARIO.md) ·
[Portfolio case study](docs/CASO_DE_ESTUDIO_PORTAFOLIO.md) · [Final report](docs/INFORME_CIERRE_DATATRUST_V1_CODEX.md)

## Problem, audience, and value

Order imports often fail late because of duplicate identifiers, malformed
emails, out-of-policy amounts, unexpected currencies, or impossible dates.
This prototype moves those checks earlier and produces a reproducible diagnosis
before data reaches another system.

It is intended for students, technical reviewers, and small teams exploring
local data-quality workflows. Its demonstrable value is concrete:

- explicit, versioned rules instead of opaque decisions;
- valid/invalid row metrics and issue-level explanations;
- local history, pagination, and formula-safe CSV export;
- data minimization: original rows and filenames are not persisted;
- automated coverage for boundaries, privacy, Unicode, SQLite, and real HTTP.

No real customers, financial savings, or company adoption are claimed.

## Demo flow

1. Select `orders_v1` or `orders_usd_v1`.
2. Upload a UTF-8 CSV; the API checks structure, limits, and row rules.
3. SQLite stores only a technical summary and issues, never source rows.
4. Review metrics, history, pages, and the safe issue export.

An **invalid row** can have several **issues**, so the two counts may differ.

## Architecture and stack

```text
Local browser
  └── FastAPI / Starlette (HTTP, ASGI, static dashboard)
        ├── profiles.py + JSON (allow-listed profiles)
        ├── validator.py (pure rules and Decimal)
        ├── store.py (parameterized SQL and transactions)
        └── SQLite (summaries and issues)
```

- Python 3.11+; the final local verification used Python 3.12.14.
- FastAPI 0.162.0, Starlette 1.10.0, Uvicorn 0.54.0, Pydantic 2.14.1.
- SQLite 3.53.1 during final verification.
- Plain HTML, CSS, and JavaScript; pytest 9.1.1 and httpx2 2.16.0.

## Actual limits

- CSV file: **2 MiB** and **10,000 data rows**.
- Multipart request: default ASGI limit is 2 MiB + 64 KiB, allowing HTTP
  envelope overhead while the file limit remains exactly 2 MiB.
- UTF-8 input; a UTF-8 BOM is accepted.
- File-backed SQLite, one process, and `--workers 1`.
- One local user; no authentication, authorization, TLS, or tenant isolation.
- No encryption at rest, enterprise retention, or schema migrations.
- Extension and MIME are hints; CSV structure and rules are authoritative.

## Quick start on Windows PowerShell

```powershell
cd <LOCAL_PATH>\DataTrust_API_Starter
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest -q
.\scripts\iniciar_demo.ps1
```

The launcher neither downloads software nor changes PowerShell policy. If your
environment does not allow scripts, use the equivalent direct command:

```powershell
.\.venv\Scripts\python.exe -m uvicorn datatrust_api.main:app --host 127.0.0.1 --port 8000 --workers 1
```

Open `http://127.0.0.1:8000/` and stop the server with `Ctrl+C`. Python 3.12
users can reproduce the verified dependency snapshot with:

```powershell
.\.venv\Scripts\python.exe -m pip install -c constraints\verified-py312.txt -e ".[dev]"
```

## macOS or Linux

```bash
cd /local/path/DataTrust_API_Starter
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m pytest -q
.venv/bin/python -m uvicorn datatrust_api.main:app --host 127.0.0.1 --port 8000 --workers 1
```

macOS/Linux was not locally verified in this closing cycle. The CI file declares
Python 3.11/3.12, but no remote CI result is claimed.

## Included synthetic datasets

Both files can be downloaded from the dashboard and are included in the wheel:

| File | Profile | Total | Valid | Invalid | Issues |
|---|---|---:|---:|---:|---:|
| `static/demo-orders-6.csv` | `orders_v1` | 6 | 2 | 4 | 5 |
| `static/demo-orders-100.csv` | `orders_v1` | 100 | 90 | 10 | 10 |

The six-order sample demonstrates duplicate ID, email, amount, currency, and
date findings. The 100-order sample has 90 valid rows and 10 synthetic invalid
emails, one per row. All addresses use the reserved `example.invalid` domain.

## API surface

| Method and path | Result |
|---|---|
| `GET /` | local dashboard |
| `GET /docs` | interactive OpenAPI |
| `GET /health` | health and version |
| `GET /api/v1/profiles` | allowed profiles |
| `POST /api/v1/runs?profile=orders_v1` | validate a multipart CSV |
| `GET /api/v1/runs?limit=20&offset=0` | paginated history |
| `GET /api/v1/runs/{id}` | summary and first 100 issues |
| `GET /api/v1/runs/{id}/issues` | paginated issues |
| `GET /api/v1/runs/{id}/issues.csv` | complete safe export |

Abbreviated `201` response:

```json
{
  "id": "8f1c...",
  "filename": "8f1c....csv",
  "profile": "orders_v1",
  "status": "completed",
  "total_rows": 6,
  "valid_rows": 2,
  "invalid_rows": 4,
  "issue_count": 5,
  "created_at": "2026-10-27T18:00:00+00:00"
}
```

`filename` is a neutral UUID-based technical name. Expected errors use 413
(size), 415 (extension), 422 (structure/parameters), 503 with `Retry-After: 1`
(SQLite contention), and 404 for unknown runs.

## Testing and evidence

The final local run discovered and passed **113 tests** with no warnings:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m compileall -q src tests scripts
node --check src\datatrust_api\static\app.js
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe scripts\smoke_http_e2e.py
```

A `1.0.0` wheel was installed in a separate environment and its resources were
loaded. Real browser tests covered 360×800, 390×844, 768×1024, and 1366×768.
See [VERIFICACION.md](docs/VERIFICACION.md) and [BENCHMARK.md](docs/BENCHMARK.md).
The benchmark is a local engineering measurement, not an SLA.

## Security and privacy

The project uses parameterized SQL, explicit transactions and connection
closure, a byte-counting ASGI limit, thread-pool delegation for validation and
SQLite writes, defensive browser headers, `textContent` for untrusted text, and
formula neutralization on CSV export. It does not store original rows or source
filenames.

These controls improve a local demo; they do not make it suitable for public
production. Do not upload real or sensitive data.

## Authorship and process

Personal project by **Yerlan Daniel Gómez Hernández**
([GitHub: yerlangomezhernandez24-afk](https://github.com/yerlangomezhernandez24-afk)).
The owner directed and validated the project with AI-assisted review, testing,
and documentation. The application itself contains no AI model; its rules are
deterministic and reproducible.

## Frozen scope and publication status

`v1.0.0` freezes the local portfolio product. Only concrete blocking defects
should reopen it. Authentication, TLS, tenant isolation, retention,
observability, migrations, and a measured WAL/server-database strategy would be
a separate product scope.

The public identity, GitHub `noreply` address, and target repository are
defined. Publication remains pending until the initial commit is created and
Git is authenticated from this computer. See
[DATOS_PENDIENTES_PUBLICACION.md](docs/DATOS_PENDIENTES_PUBLICACION.md) and
[CHECKLIST_PUBLICACION_GITHUB.md](docs/CHECKLIST_PUBLICACION_GITHUB.md). No
`LICENSE` file is included because the owner has not selected one.
