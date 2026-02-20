# ─── Stage 1: Build Vue frontend ─────────────────────────────────────────────
FROM node:22-alpine AS frontend-builder

WORKDIR /build/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# ─── Stage 2: Production image ────────────────────────────────────────────────
FROM python:3.10-slim

WORKDIR /app

# Install wisecity SDK directly from GitHub (no PyPI release)
RUN apt-get update && apt-get install -y --no-install-recommends git \
    && pip install --no-cache-dir git+https://github.com/CarloGauss33/wisecity-gps-sdk.git \
    && apt-get purge -y --auto-remove git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy API source
COPY api/ ./api/

# Copy built frontend from Stage 1
COPY --from=frontend-builder /build/frontend/dist ./frontend/dist

# Volume for persistent DuckDB data
VOLUME ["/app/data"]

# Point database to the persistent volume
ENV DB_PATH=/app/data/gps.duckdb

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
