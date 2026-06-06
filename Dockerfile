# === Stage 1: Builder ===
FROM python:3.13-slim AS builder

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./

# Dependencies ko seedhe system site-packages mein install karo (no venv needed here)
RUN uv pip install --system --no-cache -r pyproject.toml

# === Stage 2: Final Runtime ===
FROM python:3.12-slim

WORKDIR /app

# AWS Lambda Web Adapter copy karo
COPY --from=public.ecr.aws/awsguru/aws-lambda-adapter:0.8.4 /lambda-adapter /opt/extensions/lambda-adapter

# Builder stage se saari installed packages copy karo
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

ENV PORT=8080 \
    AWS_LWA_INVOKE_MODE=response_stream \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Apni application files copy karo
COPY main.py ./
COPY router ./router

EXPOSE 8080

# Seedhe uvicorn ko call karo binary array format mein (No sh, no uv, no venv)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]