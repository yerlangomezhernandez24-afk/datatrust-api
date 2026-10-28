import asyncio

import pytest
from fastapi.testclient import TestClient

from datatrust_api.main import (
    DEFAULT_MAX_REQUEST_BYTES,
    MAX_FILE_BYTES,
    RequestBodyLimitMiddleware,
    create_app,
)


def invoke_asgi(app, body_chunks, headers):
    messages = [
        {
            "type": "http.request",
            "body": chunk,
            "more_body": index < len(body_chunks) - 1,
        }
        for index, chunk in enumerate(body_chunks)
    ]
    sent = []

    async def receive():
        return messages.pop(0)

    async def send(message):
        sent.append(message)

    scope = {
        "type": "http",
        "asgi": {"version": "3.0", "spec_version": "2.3"},
        "http_version": "1.1",
        "method": "POST",
        "scheme": "http",
        "path": "/api/v1/runs",
        "raw_path": b"/api/v1/runs",
        "query_string": b"",
        "root_path": "",
        "headers": headers,
        "client": ("127.0.0.1", 12345),
        "server": ("testserver", 80),
    }
    asyncio.run(app(scope, receive, send))
    return sent


def response_status(messages):
    return next(message["status"] for message in messages if message["type"] == "http.response.start")


def multipart_body(total_size):
    prefix = (
        b"--t105-boundary\r\n"
        b'Content-Disposition: form-data; name="file"; filename="orders.csv"\r\n'
        b"Content-Type: text/csv\r\n\r\n"
    )
    suffix = b"\r\n--t105-boundary--\r\n"
    assert total_size > len(prefix) + len(suffix)
    return prefix + (b"x" * (total_size - len(prefix) - len(suffix))) + suffix


def test_request_limit_is_separate_from_csv_limit_and_prevents_persistence(tmp_path):
    request_limit = MAX_FILE_BYTES + 64
    app = create_app(str(tmp_path / "request-limit.db"), max_request_bytes=request_limit)

    with TestClient(app) as client:
        request = client.build_request(
            "POST",
            "/api/v1/runs",
            files={"file": ("limit.csv", b"x" * MAX_FILE_BYTES, "text/csv")},
        )
        assert int(request.headers["content-length"]) > request_limit

        response = client.send(request)

        assert response.status_code == 413, response.text
        assert client.get("/api/v1/runs").json() == []


@pytest.mark.parametrize(
    "content_length",
    [None, b"1", b"not-a-number"],
    ids=["missing", "falsely-low", "invalid"],
)
def test_fragmented_request_is_limited_by_actual_bytes_without_trusting_header(
    tmp_path, content_length
):
    request_limit = MAX_FILE_BYTES + 128
    body = multipart_body(request_limit + 1)
    headers = [(b"content-type", b"multipart/form-data; boundary=t105-boundary")]
    if content_length is not None:
        headers.append((b"content-length", content_length))
    chunks = [body[:700_000], body[700_000:1_400_000], body[1_400_000:]]
    app = create_app(str(tmp_path / "fragmented.db"), max_request_bytes=request_limit)

    messages = invoke_asgi(app, chunks, headers)

    assert response_status(messages) == 413


def test_declared_oversize_is_rejected_before_reading_body(tmp_path):
    request_limit = DEFAULT_MAX_REQUEST_BYTES
    read_calls = 0
    sent = []

    async def receive():
        nonlocal read_calls
        read_calls += 1
        return {"type": "http.request", "body": b"small", "more_body": False}

    async def send(message):
        sent.append(message)

    scope = {
        "type": "http",
        "asgi": {"version": "3.0", "spec_version": "2.3"},
        "http_version": "1.1",
        "method": "POST",
        "scheme": "http",
        "path": "/api/v1/runs",
        "raw_path": b"/api/v1/runs",
        "query_string": b"",
        "root_path": "",
        "headers": [(b"content-length", str(request_limit + 1).encode())],
        "client": ("127.0.0.1", 12345),
        "server": ("testserver", 80),
    }
    app = create_app(str(tmp_path / "declared.db"), max_request_bytes=request_limit)

    asyncio.run(app(scope, receive, send))

    assert response_status(sent) == 413
    assert read_calls == 0


def test_middleware_accepts_exact_fragmented_limit_and_rejects_next_byte():
    received_sizes = []

    async def probe(scope, receive, send):
        total = 0
        while True:
            message = await receive()
            total += len(message.get("body", b""))
            if not message.get("more_body", False):
                break
        received_sizes.append(total)
        await send({"type": "http.response.start", "status": 204, "headers": []})
        await send({"type": "http.response.body", "body": b""})

    middleware = RequestBodyLimitMiddleware(probe, max_body_bytes=10)
    accepted = invoke_asgi(middleware, [b"123", b"4567", b"890"], [])
    rejected = invoke_asgi(middleware, [b"12345", b"67890", b"x"], [])

    assert response_status(accepted) == 204
    assert response_status(rejected) == 413
    assert received_sizes == [10]
