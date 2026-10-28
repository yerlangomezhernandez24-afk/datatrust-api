"""Smoke E2E real por HTTP contra Uvicorn en loopback y SQLite temporal."""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path


def _free_loopback_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


def _request(base_url: str, path: str, *, method: str = "GET", body=None, headers=None):
    request = urllib.request.Request(
        base_url + path,
        data=body,
        headers=headers or {},
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return (
                response.status,
                {key.lower(): value for key, value in response.headers.items()},
                response.read(),
            )
    except urllib.error.HTTPError as error:
        return (
            error.code,
            {key.lower(): value for key, value in error.headers.items()},
            error.read(),
        )


def _wait_until_ready(base_url: str, process: subprocess.Popen) -> None:
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        if process.poll() is not None:
            output = process.stdout.read() if process.stdout else ""
            raise RuntimeError(f"Uvicorn terminó antes del smoke: {output[-2000:]}")
        try:
            status, _, _ = _request(base_url, "/health")
            if status == 200:
                return
        except OSError:
            pass
        time.sleep(0.05)
    raise RuntimeError("Uvicorn no respondió en loopback dentro de 10 segundos.")


def _multipart_csv(csv_content: bytes) -> tuple[bytes, dict[str, str]]:
    boundary = "datatrust-local-e2e-boundary"
    body = (
        f"--{boundary}\r\n"
        'Content-Disposition: form-data; name="file"; filename="synthetic.csv"\r\n'
        "Content-Type: text/csv\r\n\r\n"
    ).encode() + csv_content + f"\r\n--{boundary}--\r\n".encode()
    return body, {"Content-Type": f"multipart/form-data; boundary={boundary}"}


def run_smoke() -> dict[str, object]:
    host = "127.0.0.1"
    port = _free_loopback_port()
    base_url = f"http://{host}:{port}"
    result: dict[str, object] = {"host": host}
    root_path: Path | None = None

    with tempfile.TemporaryDirectory(prefix="datatrust-http-e2e-") as directory:
        root_path = Path(directory)
        database = root_path / "synthetic.sqlite3"
        environment = os.environ.copy()
        environment["DATATRUST_DB"] = str(database)
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "datatrust_api.main:app",
                "--host",
                host,
                "--port",
                str(port),
                "--workers",
                "1",
            ],
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        try:
            _wait_until_ready(base_url, process)
            health_status, health_headers, health_body = _request(base_url, "/health")
            dashboard_status, dashboard_headers, dashboard_body = _request(base_url, "/")
            profiles_status, _, profiles_body = _request(base_url, "/api/v1/profiles")
            assert json.loads(health_body)["status"] == "ok"
            assert b'id="upload-form"' in dashboard_body
            assert any(
                profile["id"] == "orders_usd_v1"
                for profile in json.loads(profiles_body)
            )

            csv_content = (
                b"order_id,customer_id,email,amount,currency,order_date\n"
                b"O1,C1,valid@example.invalid,10.00,USD,2026-10-27\n"
                b"O2,C2,invalid-email,1.234,USD,2026-02-30\n"
            )
            body, headers = _multipart_csv(csv_content)
            upload_status, _, upload_body = _request(
                base_url,
                "/api/v1/runs?profile=orders_usd_v1",
                method="POST",
                body=body,
                headers=headers,
            )
            created = json.loads(upload_body)
            run_id = created["id"]
            list_status, _, list_body = _request(base_url, "/api/v1/runs?limit=10&offset=0")
            detail_status, _, detail_body = _request(base_url, f"/api/v1/runs/{run_id}")
            first_status, _, first_body = _request(
                base_url, f"/api/v1/runs/{run_id}/issues?limit=2&offset=0"
            )
            last_status, _, last_body = _request(
                base_url, f"/api/v1/runs/{run_id}/issues?limit=2&offset=2"
            )
            export_status, export_headers, export_body = _request(
                base_url, f"/api/v1/runs/{run_id}/issues.csv"
            )
            unknown_status, _, _ = _request(base_url, "/api/v1/runs/unknown")

            oversized_body, oversized_headers = _multipart_csv(
                b"x" * (2 * 1024 * 1024 + 1)
            )
            oversized_status, _, _ = _request(
                base_url,
                "/api/v1/runs",
                method="POST",
                body=oversized_body,
                headers=oversized_headers,
            )
            _, _, list_after_oversized_body = _request(
                base_url, "/api/v1/runs?limit=10&offset=0"
            )

            assert len(json.loads(list_body)) == 1
            assert json.loads(detail_body)["issue_count"] == 3
            assert len(json.loads(first_body)) == 2
            assert len(json.loads(last_body)) == 1
            assert export_headers["content-disposition"] == (
                'attachment; filename="validation-issues.csv"'
            )
            assert b"INVALID_AMOUNT" in export_body
            result.update(
                {
                    "health": health_status,
                    "dashboard": dashboard_status,
                    "security_headers": {
                        "health_nosniff": health_headers.get("x-content-type-options"),
                        "dashboard_frame_options": dashboard_headers.get("x-frame-options"),
                    },
                    "profiles": profiles_status,
                    "upload": upload_status,
                    "selected_profile": created["profile"],
                    "list": list_status,
                    "detail": detail_status,
                    "first_issue_page": first_status,
                    "last_issue_page": last_status,
                    "export": export_status,
                    "export_has_bom": export_body.startswith(b"\xef\xbb\xbf"),
                    "unknown_run": unknown_status,
                    "oversized_upload": oversized_status,
                    "oversized_upload_persisted": len(
                        json.loads(list_after_oversized_body)
                    )
                    != 1,
                }
            )
        finally:
            process.terminate()
            try:
                process.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate(timeout=5)

    result["temporary_database_removed"] = root_path is not None and not root_path.exists()
    return result


def main() -> int:
    print(json.dumps(run_smoke(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
