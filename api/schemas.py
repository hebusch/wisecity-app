"""Pydantic response models."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class LocationPoint(BaseModel):
    latitude: Optional[float]
    longitude: Optional[float]


class VehicleInfo(BaseModel):
    plate: Optional[str]
    brand: Optional[str]
    model: Optional[str]
    year: Optional[int]


class DeviceResponse(BaseModel):
    id: str
    name: Optional[str]
    vehicle: VehicleInfo
    location: LocationPoint
    status_name: Optional[str]
    speed: float
    last_update: Optional[str]
    locked: bool
    google_maps_url: Optional[str]


class LocationRecord(BaseModel):
    id: int
    device_id: str
    plate: Optional[str]
    latitude: float
    longitude: float
    speed: float
    status_name: Optional[str]
    timestamp: datetime


class TripRecord(BaseModel):
    trip_num: int
    start_time: datetime
    end_time: datetime
    distance_km: float
    duration_min: float
    avg_speed: Optional[float]
    max_speed: float


class StatsResponse(BaseModel):
    total_trips: int
    total_km: float
    total_hours: float
    avg_speed: Optional[float]
    max_speed: Optional[float]
