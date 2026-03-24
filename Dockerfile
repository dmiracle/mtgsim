# =============================================================================
# Stage 1: Build frontend
# =============================================================================
FROM node:22-slim AS frontend-build

WORKDIR /app/frontend
COPY mtgsim/frontend/package.json mtgsim/frontend/package-lock.json* ./
RUN npm ci
COPY mtgsim/frontend/ ./
RUN npm run build

# =============================================================================
# Stage 2: Python API
# =============================================================================
FROM python:3.14-slim AS api

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy dependency packages first (better layer caching)
COPY mtgsim/packages/mtgdb/ /app/packages/mtgdb/
COPY srs/ /app/srs/
COPY llmex/ /app/llmex/

# Copy project config — rewrite sibling paths to in-container paths
COPY mtgsim/pyproject.toml mtgsim/uv.lock ./

# Copy source
COPY mtgsim/src/ /app/src/

# Rewrite path dependencies to match container layout
RUN sed -i 's|path = "\.\./srs"|path = "/app/srs"|' pyproject.toml && \
    sed -i 's|path = "\.\./llmex"|path = "/app/llmex"|' pyproject.toml

# Install dependencies
RUN uv sync --frozen --no-dev || uv sync --no-dev

# Copy static assets
COPY mtgsim/web/ /app/web/
COPY mtgsim/resources/ /app/resources/
COPY --from=frontend-build /app/frontend/dist/ /app/webapp/

# Create data directory
RUN mkdir -p /data/mtgsim /data/srs

# Environment
ENV PYTHONUNBUFFERED=1

EXPOSE 8001

CMD ["uv", "run", "mtgsim-api", "--host", "0.0.0.0", "--port", "8001"]
