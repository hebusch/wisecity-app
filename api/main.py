"""FastAPI application entry point with integrated GPS collector."""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

load_dotenv()

from api import database
from api.routes import auth, devices, locations, passkey, trips, stats

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Collector background task
# ---------------------------------------------------------------------------

async def run_collector() -> None:
    """Poll WiseCity API every 60 s and persist locations to DuckDB.

    Credentials come from the first active session in memory — no env vars needed.
    If no user is logged in the cycle is skipped silently.
    """
    from wisecity import WiseCityClient
    from wisecity.exceptions import WiseCityError
    from api.routes.auth import _sessions

    log.info("Collector started (polling every 60 s)")

    while True:
        # Grab credentials from any active session
        creds = next(iter(_sessions.values()), None)
        if creds is None:
            log.debug("Collector: no active session, skipping poll")
            await asyncio.sleep(60)
            continue

        email, password = creds
        try:
            client = WiseCityClient(email=email, password=password)
            devices_list = await asyncio.to_thread(client.devices.list)
            saved = 0
            for device in devices_list:
                loc = device.location
                if loc.latitude is None or loc.longitude is None:
                    continue
                if not device.last_update:
                    continue
                database.insert_location(
                    device_id=device.id,
                    plate=device.vehicle.plate,
                    latitude=loc.latitude,
                    longitude=loc.longitude,
                    speed=device.speed or 0.0,
                    status_name=device.status_name,
                    timestamp=device.last_update,
                )
                saved += 1
            log.info("Collector: saved %d location(s)", saved)
        except WiseCityError as exc:
            log.warning("Collector API error: %s", exc)
        except Exception as exc:  # noqa: BLE001
            log.exception("Collector unexpected error: %s", exc)

        await asyncio.sleep(60)


# ---------------------------------------------------------------------------
# App lifespan
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure schema exists before anything else
    database.get_connection()

    task = asyncio.create_task(run_collector())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(title="WiseCity GPS Dashboard", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(passkey.router, prefix="/api")
app.include_router(devices.router, prefix="/api")
app.include_router(locations.router, prefix="/api")
app.include_router(trips.router, prefix="/api")
app.include_router(stats.router, prefix="/api")

# Serve built frontend if dist/ exists
DIST = Path(__file__).parent.parent / "frontend" / "dist"
if DIST.exists():
    app.mount("/", StaticFiles(directory=str(DIST), html=True), name="frontend")
