"""GET /api/trips — trip detection via SQL window functions on DuckDB."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from api import database
from api.routes.auth import get_auth
from api.schemas import TripRecord

router = APIRouter()


@router.get("/trips", response_model=list[TripRecord])
async def get_trips(
    device_id: str = Query(..., description="Device ID"),
    days: int = Query(default=30, ge=1, le=365, description="Look-back window in days"),
    _: tuple = Depends(get_auth),
) -> list[TripRecord]:
    rows = database.query_trips(device_id, days)
    return [TripRecord(**row) for row in rows]
