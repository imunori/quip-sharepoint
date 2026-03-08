# Stage 1: Build frontend
FROM oven/bun:1 AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/bun.lock ./
RUN bun install --frozen-lockfile
COPY frontend/ .
RUN bun run build

# Stage 2: Backend + serve frontend static files
FROM python:3.13-slim

WORKDIR /app

# Install curl (for health check) and uv
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir uv

# Install backend deps
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --no-dev

# Copy backend source
COPY backend/src/ src/

# Copy built frontend
COPY --from=frontend-build /app/frontend/dist /app/static

# Create non-root user and data directories
RUN useradd -m -u 1000 appuser && mkdir -p data storage && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run with static file serving enabled
CMD ["uv", "run", "uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
