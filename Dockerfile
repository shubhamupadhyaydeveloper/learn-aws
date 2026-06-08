FROM python:3.13-slim AS builder

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./

RUN uv pip install --system --no-cache -r pyproject.toml

# stage 2
FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

ENV PORT=8080 

COPY main.py ./
COPY router ./router

EXPOSE 8080

# Seedhe uvicorn ko call karo binary array format mein (No sh, no uv, no venv)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]