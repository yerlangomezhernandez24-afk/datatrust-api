"""Endpoints REST v1. Uso local educativo; no es una API pública multiusuario."""
from __future__ import annotations

import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.responses import JSONResponse
from starlette.responses import StreamingResponse

from . import __version__
from .csv_export import iter_issue_csv
from .models import IssueOut, ProfileOut, RunDetail, RunOut
from .profiles import UnknownProfile, get_profile, list_profiles
from .store import (
    StorageBusyError,
    get_issues,
    get_run,
    init_db,
    iter_issues,
    list_runs,
    save_run,
)
from .validator import InvalidDataset, validate_orders_csv

MAX_FILE_BYTES = 2 * 1024 * 1024
DEFAULT_MAX_REQUEST_BYTES = MAX_FILE_BYTES + (64 * 1024)
MAX_SQLITE_OFFSET = 2**63 - 1
STATIC_DIR = Path(__file__).parent / "static"


class _RequestBodyTooLarge(Exception):
    """Señal interna emitida antes de entregar un chunk excesivo al parser."""


class RequestBodyLimitMiddleware:
    """Limita bytes ASGI reales antes de que Starlette procese el multipart."""

    def __init__(self, app: Any, max_body_bytes: int) -> None:
        if max_body_bytes <= 0:
            raise ValueError("El límite del request debe ser mayor que cero.")
        self.app = app
        self.max_body_bytes = max_body_bytes

    async def _reject(self, scope, receive, send) -> None:
        response = JSONResponse(
            status_code=413,
            content={
                "detail": (
                    "Solicitud demasiado grande; máximo "
                    f"{self.max_body_bytes} bytes para el cuerpo HTTP."
                )
            },
        )
        await response(scope, receive, send)

    async def __call__(self, scope, receive, send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        declared_lengths = [
            value
            for name, value in scope.get("headers", [])
            if name.lower() == b"content-length"
        ]
        if len(declared_lengths) == 1:
            try:
                declared_length = int(declared_lengths[0])
            except ValueError:
                declared_length = None
            if declared_length is not None and declared_length > self.max_body_bytes:
                await self._reject(scope, receive, send)
                return

        received_bytes = 0
        body_too_large = False
        response_started = False

        async def limited_receive():
            nonlocal body_too_large, received_bytes
            message = await receive()
            if message["type"] == "http.request":
                received_bytes += len(message.get("body", b""))
                if received_bytes > self.max_body_bytes:
                    body_too_large = True
                    raise _RequestBodyTooLarge
            return message

        async def tracked_send(message):
            nonlocal response_started
            if body_too_large:
                return
            if message["type"] == "http.response.start":
                response_started = True
            await send(message)

        try:
            await self.app(scope, limited_receive, tracked_send)
        except _RequestBodyTooLarge:
            if response_started:
                return
            await self._reject(scope, receive, send)
            return
        if body_too_large and not response_started:
            await self._reject(scope, receive, send)


class SecurityHeadersMiddleware:
    """Añade cabeceras defensivas sin bufferizar respuestas o streams."""

    def __init__(self, app: Any) -> None:
        self.app = app

    async def __call__(self, scope, receive, send) -> None:
        async def send_with_headers(message):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                names = {name.lower() for name, _ in headers}
                for name, value in (
                    (b"x-content-type-options", b"nosniff"),
                    (b"referrer-policy", b"no-referrer"),
                    (b"x-frame-options", b"DENY"),
                ):
                    if name not in names:
                        headers.append((name, value))
                message = dict(message, headers=headers)
            await send(message)

        await self.app(scope, receive, send_with_headers)


def _request_limit_from_environment(value: int | None) -> int:
    if value is None:
        configured = os.environ.get("DATATRUST_MAX_REQUEST_BYTES")
        if configured is None:
            value = DEFAULT_MAX_REQUEST_BYTES
        else:
            try:
                value = int(configured)
            except ValueError as exc:
                raise ValueError(
                    "DATATRUST_MAX_REQUEST_BYTES debe ser un entero de bytes."
                ) from exc
    if value <= MAX_FILE_BYTES:
        raise ValueError(
            "El límite del request debe ser mayor que el límite CSV de 2 MiB."
        )
    return value


def create_app(
    db_path: str | None = None,
    max_request_bytes: int | None = None,
) -> FastAPI:
    db_path = db_path if db_path is not None else os.environ.get("DATATRUST_DB", "./data/datatrust.sqlite3")
    request_limit = _request_limit_from_environment(max_request_bytes)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        init_db(db_path)
        yield

    app = FastAPI(
        title="DataTrust API", version=__version__,
        description="Valida pedidos CSV mediante reglas reproducibles; sin IA comercial ni datos originales almacenados.",
        lifespan=lifespan,
    )
    app.add_middleware(RequestBodyLimitMiddleware, max_body_bytes=request_limit)
    app.add_middleware(SecurityHeadersMiddleware)
    app.state.max_request_bytes = request_limit
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.exception_handler(StorageBusyError)
    async def storage_busy_handler(_request, _exc):
        return JSONResponse(
            status_code=503,
            content={
                "detail": "Almacenamiento local ocupado; intente nuevamente."
            },
            headers={"Retry-After": "1"},
        )

    @app.get("/", include_in_schema=False)
    def dashboard():
        return FileResponse(
            STATIC_DIR / "index.html",
            headers={
                "Cache-Control": "no-store",
                "Content-Security-Policy": (
                    "default-src 'self'; script-src 'self'; style-src 'self'; "
                    "img-src 'self'; connect-src 'self'; base-uri 'none'; "
                    "frame-ancestors 'none'; form-action 'self'"
                ),
            },
        )

    @app.get("/health", tags=["Sistema"])
    def health():
        return {"status": "ok", "version": __version__}

    @app.get("/api/v1/profiles", response_model=list[ProfileOut], tags=["Perfiles"])
    def profiles():
        return [profile.summary() for profile in list_profiles()]

    @app.post("/api/v1/runs", response_model=RunOut, status_code=201, tags=["Validaciones"])
    async def validate_csv(
        file: UploadFile = File(..., description="Archivo CSV UTF-8; máximo 2 MiB"),
        profile_id: str = Query("orders_v1", alias="profile"),
    ):
        try:
            selected_profile = get_profile(profile_id)
        except UnknownProfile as exc:
            raise HTTPException(422, str(exc)) from exc
        try:
            original_filename = Path((file.filename or "").replace("\\", "/")).name
            if Path(original_filename).suffix.casefold() != ".csv":
                raise HTTPException(415, "Se aceptan únicamente archivos .csv")
            raw = await file.read(MAX_FILE_BYTES + 1)
        finally:
            await file.close()
        if len(raw) > MAX_FILE_BYTES:
            raise HTTPException(413, "Archivo demasiado grande; máximo 2 MiB.")
        try:
            total, valid, issues = await run_in_threadpool(
                validate_orders_csv, raw, selected_profile
            )
        except InvalidDataset as exc:
            raise HTTPException(422, str(exc)) from exc
        run_id = str(uuid4())
        run = {
            "id": run_id, "filename": f"{run_id}.csv", "profile": selected_profile.id,
            "status": "completed", "total_rows": total, "valid_rows": valid,
            "invalid_rows": total - valid, "issue_count": len(issues),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        try:
            await run_in_threadpool(save_run, db_path, run, issues)
        except StorageBusyError as exc:
            raise HTTPException(
                503,
                "Almacenamiento local ocupado; intente nuevamente.",
                headers={"Retry-After": "1"},
            ) from exc
        return run

    @app.get("/api/v1/runs", response_model=list[RunOut], tags=["Validaciones"])
    def runs(
        limit: int = Query(20, ge=1, le=100),
        offset: int = Query(0, ge=0, le=MAX_SQLITE_OFFSET),
    ):
        return list_runs(db_path, limit, offset)

    @app.get("/api/v1/runs/{run_id}", response_model=RunDetail, tags=["Validaciones"])
    def run_detail(run_id: str):
        run = get_run(db_path, run_id)
        if run is None:
            raise HTTPException(404, "Ejecución no encontrada.")
        return dict(run, issues=get_issues(db_path, run_id, 100, 0))

    @app.get("/api/v1/runs/{run_id}/issues.csv", tags=["Validaciones"])
    def export_run_issues(run_id: str):
        if get_run(db_path, run_id) is None:
            raise HTTPException(404, "Ejecución no encontrada.")
        return StreamingResponse(
            iter_issue_csv(iter_issues(db_path, run_id)),
            media_type="text/csv; charset=utf-8",
            headers={
                "Content-Disposition": (
                    'attachment; filename="validation-issues.csv"'
                )
            },
        )

    @app.get("/api/v1/runs/{run_id}/issues", response_model=list[IssueOut], tags=["Validaciones"])
    def run_issues(
        run_id: str,
        limit: int = Query(100, ge=1, le=500),
        offset: int = Query(0, ge=0, le=MAX_SQLITE_OFFSET),
    ):
        if get_run(db_path, run_id) is None:
            raise HTTPException(404, "Ejecución no encontrada.")
        return get_issues(db_path, run_id, limit, offset)

    return app


app = create_app()
