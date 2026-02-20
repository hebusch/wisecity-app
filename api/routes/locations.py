"""GET /api/locations — raw location history from DuckDB."""

from __future__ import annotations

from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, Query

from api import database
from api.routes.auth import get_auth
from api.schemas import LocationRecord

router = APIRouter()


@router.get("/locations", response_model=list[LocationRecord])
async def get_locations(
    device_id: str = Query(..., description="Device ID"),
    from_ts: str = Query(
        default=None,
        description="Start timestamp (ISO 8601). Defaults to 24 hours ago.",
    ),
    to_ts: str = Query(
        default=None,
        description="End timestamp (ISO 8601). Defaults to now.",
    ),
    _: tuple = Depends(get_auth),
) -> list[LocationRecord]:
    now = datetime.now(timezone.utc)
    resolved_from = from_ts or (now - timedelta(hours=24)).isoformat()
    resolved_to = to_ts or now.isoformat()

    rows = database.query_locations(device_id, resolved_from, resolved_to)
    return [LocationRecord(**row) for row in rows]
