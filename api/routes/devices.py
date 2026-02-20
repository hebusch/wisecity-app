"""GET /api/devices — live proxy to WiseCity API."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from wisecity import WiseCityClient
from wisecity.exceptions import WiseCityError

from api.routes.auth import get_wisecity_client
from api.schemas import DeviceResponse, LocationPoint, VehicleInfo

router = APIRouter()


@router.get("/devices", response_model=list[DeviceResponse])
async def list_devices(
    client: WiseCityClient = Depends(get_wisecity_client),
) -> list[DeviceResponse]:
    """Return live device list from WiseCity API."""
    try:
        devices = client.devices.list()
    except WiseCityError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    result = []
    for d in devices:
        result.append(DeviceResponse(
            id=d.id,
            name=d.name,
            vehicle=VehicleInfo(
                plate=d.vehicle.plate,
                brand=d.vehicle.brand,
                model=d.vehicle.model,
                year=d.vehicle.year,
            ),
            location=LocationPoint(
                latitude=d.location.latitude,
                longitude=d.location.longitude,
            ),
            status_name=d.status_name,
            speed=d.speed,
            last_update=d.last_update,
            locked=d.locked,
            google_maps_url=d.location.google_maps_url or None,
        ))
    return result
