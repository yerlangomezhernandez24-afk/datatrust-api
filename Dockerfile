FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATATRUST_DB=/app/data/datatrust.sqlite3
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src/ src/
RUN pip install --no-cache-dir .
RUN addgroup --system datatrust \
    && adduser --system --ingroup datatrust --no-create-home datatrust \
    && mkdir -p /app/data \
    && chown -R datatrust:datatrust /app/data
USER datatrust
EXPOSE 8000
# 0.0.0.0 es interno al contenedor. Publicar solo con -p 127.0.0.1:8000:8000.
# SOLO DEMO LOCAL: un worker, sin autenticación ni protección empresarial.
CMD ["uvicorn", "datatrust_api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
