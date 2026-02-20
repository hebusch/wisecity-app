# WiseCity GPS Dashboard

A self-hosted GPS tracking dashboard for WiseCity devices. Polls the WiseCity API, stores location history in DuckDB, and serves a Vue 3 map interface with trip history and statistics.

## Features

- Real-time vehicle location on an interactive Leaflet map
- Multi-device support with device switcher
- Trip history with colored speed polylines
- 30-day statistics (trips, km, hours, avg/max speed)
- Dark / light mode
- Progressive Web App (PWA) — installable on mobile
- Session-based login (credentials never stored in the browser)

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Vue 3 + TypeScript, Vite, Leaflet |
| Backend | FastAPI, Python 3.10 |
| Database | DuckDB (embedded, file-based) |
| GPS SDK | [wisecity-gps-sdk](https://github.com/CarloGauss33/wisecity-gps-sdk) |
| Container | Docker + Docker Compose |

## Quick Start (Docker)

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd wisecity-app
```

### 2. Configure environment (optional)

```bash
cp .env.example .env
```

The default values work out of the box. Edit `.env` only if you want to change the database path.

### 3. Build and run

```bash
docker compose up --build
```

The app will be available at **http://localhost:8000**.

> On first startup the background collector begins polling the WiseCity API every 60 seconds. Location history accumulates over time.

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DB_PATH` | No | `/app/data/gps.duckdb` | Path to the DuckDB database file |

> The Docker Compose setup mounts a named volume at `/app/data` so the database persists across container restarts.

WiseCity credentials are entered at login time and are never stored on disk.

## Local Development

### Backend

```bash
python -m venv .venv
source .venv/bin/activate

pip install git+https://github.com/CarloGauss33/wisecity-gps-sdk.git
pip install -r requirements.txt

uvicorn api.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server proxies `/api` requests to `http://localhost:8000`, so both can run simultaneously.

## Project Structure

```
wisecity-app/
├── api/
│   ├── main.py              # FastAPI app, background collector
│   ├── database.py          # DuckDB schema and queries
│   ├── schemas.py           # Pydantic models
│   └── routes/
│       ├── auth.py          # Session-based login/logout
│       ├── devices.py       # Live device positions
│       ├── locations.py     # Raw location history
│       ├── trips.py         # Trip detection and listing
│       └── stats.py         # 30-day statistics
├── frontend/
│   ├── src/
│   │   ├── App.vue
│   │   ├── views/
│   │   │   └── LoginView.vue
│   │   ├── components/
│   │   │   ├── MapView.vue
│   │   │   ├── TopBar.vue
│   │   │   ├── BottomBar.vue
│   │   │   ├── Dashboard.vue
│   │   │   ├── DeviceSelector.vue
│   │   │   └── SpeedLegend.vue
│   │   └── composables/
│   │       ├── useAuth.ts
│   │       ├── useDevices.ts
│   │       └── useTrips.ts
│   └── package.json
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/auth/login` | Authenticate and obtain session token |
| `POST` | `/api/auth/logout` | Invalidate session token |
| `GET` | `/api/devices` | List all devices with current position |
| `GET` | `/api/locations` | Location history for a device and time range |
| `GET` | `/api/trips` | Detected trips for a device (last 30 days) |
| `GET` | `/api/stats` | Aggregated statistics for a device |

All endpoints except `/api/auth/login` require a `Authorization: Bearer <token>` header.

## Data Persistence

DuckDB stores all location history in a single file. In the Docker setup this file lives in a named volume (`gps-data`) so it survives container rebuilds and updates.

To back up the database:

```bash
docker compose cp gps:/app/data/gps.duckdb ./backup.duckdb
```
