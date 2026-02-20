"""GET /api/stats — aggregated driving stats from DuckDB."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from api import database
from api.routes.auth import get_auth
from api.schemas import StatsResponse

router = APIRouter()


@router.get("/stats", response_model=StatsResponse)
async def get_stats(
    device_id: str = Query(..., description="Device ID"),
    days: int = Query(default=30, ge=1, le=365, description="Look-back window in days"),
    _: tuple = Depends(get_auth),
) -> StatsResponse:
    data = database.query_stats(device_id, days)
    return StatsResponse(**data)
