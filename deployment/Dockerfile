# Multi-agent Research Assistant -> Cloud Run.
# Build from the PROJECT ROOT (build context = repo root):
#   docker build -f deployment/Dockerfile -t research-assistant .
FROM python:3.13-slim

# uv for fast, reproducible installs straight from uv.lock
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# 1) Dependencies first (cached layer) — from the lockfile, no dev tools, no project
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# 2) App code + the prebuilt FAISS index (corpus PDFs are NOT needed at runtime)
COPY src/ ./src/
COPY faiss_index/ ./faiss_index/

# Cloud Run routes traffic to $PORT (default 8080). Vertex/Gemini auth comes from
# the service's GCP identity (ADC) — set GOOGLE_* + TAVILY_API_KEY as deploy env vars.
ENV PORT=8080
EXPOSE 8080
CMD ["sh", "-c", "uv run --no-sync python -m uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
