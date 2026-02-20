"""DuckDB connection, schema creation, and query helpers."""

from __future__ import annotations

import os
import asyncio
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import duckdb

DB_PATH = os.environ.get("DB_PATH", str(Path(__file__).parent.parent / "gps.duckdb"))

# Single connection protected by a lock (DuckDB is not thread-safe for writes)
_lock = threading.Lock()
_conn: duckdb.DuckDBPyConnection | None = None


def get_connection() -> duckdb.DuckDBPyConnection:
    global _conn
    if _conn is None:
        _conn = duckdb.connect(DB_PATH)
        _init_schema(_conn)
    return _conn


def _init_schema(conn: duckdb.DuckDBPyConnection) -> None:
    conn.execute("""
        CREATE SEQUENCE IF NOT EXISTS seq_loc START 1;

        CREATE TABLE IF NOT EXISTS locations (
            id          BIGINT PRIMARY KEY DEFAULT nextval('seq_loc'),
            device_id   VARCHAR NOT NULL,
            plate       VARCHAR,
            latitude    DOUBLE  NOT NULL,
            longitude   DOUBLE  NOT NULL,
            speed       DOUBLE  DEFAULT 0,
            status_name VARCHAR,
            timestamp   TIMESTAMPTZ NOT NULL,
            captured_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
        );

        CREATE UNIQUE INDEX IF NOT EXISTS idx_locations_unique
            ON locations(device_id, timestamp);
    """)


@contextmanager
def db():
    """Acquire the global DB lock and yield the connection."""
    with _lock:
        conn = get_connection()
        yield conn


def insert_location(
    device_id: str,
    plate: str | None,
    latitude: float,
    longitude: float,
    speed: float,
    status_name: str | None,
    timestamp: str,
) -> None:
    with db() as conn:
        conn.execute(
            """
            INSERT INTO locations (device_id, plate, latitude, longitude, speed, status_name, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (device_id, timestamp) DO NOTHING
            """,
            [device_id, plate, latitude, longitude, speed, status_name, timestamp],
        )


TRIPS_SQL = """
WITH gaps AS (
    SELECT *,
        LAG(timestamp) OVER w AS prev_ts,
        LAG(latitude)  OVER w AS prev_lat,
        LAG(longitude) OVER w AS prev_lng,
        CASE
            WHEN epoch(timestamp - LAG(timestamp) OVER w) > 300
              OR LAG(timestamp) OVER w IS NULL
            THEN 1
            ELSE 0
        END AS is_start
    FROM locations
    WHERE device_id = ?
      AND timestamp >= now() - INTERVAL (? || ' DAY')
    WINDOW w AS (PARTITION BY device_id ORDER BY timestamp)
),
grouped AS (
    SELECT *, SUM(is_start) OVER (ORDER BY timestamp) AS trip_num
    FROM gaps
),
haversine AS (
    SELECT *,
        6371 * 2 * ASIN(SQRT(
            POWER(SIN(RADIANS(latitude  - prev_lat) / 2), 2) +
            COS(RADIANS(prev_lat)) * COS(RADIANS(latitude)) *
            POWER(SIN(RADIANS(longitude - prev_lng) / 2), 2)
        )) AS segment_km
    FROM grouped
    WHERE prev_lat IS NOT NULL
)
SELECT
    trip_num,
    MIN(timestamp)                                                    AS start_time,
    MAX(timestamp)                                                    AS end_time,
    ROUND(SUM(segment_km), 2)                                         AS distance_km,
    ROUND(epoch(MAX(timestamp) - MIN(timestamp)) / 60.0)              AS duration_min,
    ROUND(AVG(CASE WHEN speed > 2 THEN speed END), 1)                 AS avg_speed,
    MAX(speed)                                                        AS max_speed
FROM haversine
GROUP BY trip_num
HAVING MAX(speed) > 2 AND SUM(segment_km) > 0.1
ORDER BY MIN(timestamp) DESC
"""

STATS_SQL = """
WITH gaps AS (
    SELECT *,
        LAG(timestamp) OVER w AS prev_ts,
        LAG(latitude)  OVER w AS prev_lat,
        LAG(longitude) OVER w AS prev_lng,
        CASE
            WHEN epoch(timestamp - LAG(timestamp) OVER w) > 300
              OR LAG(timestamp) OVER w IS NULL
            THEN 1
            ELSE 0
        END AS is_start
    FROM locations
    WHERE device_id = ?
      AND timestamp >= now() - INTERVAL (? || ' DAY')
    WINDOW w AS (PARTITION BY device_id ORDER BY timestamp)
),
grouped AS (
    SELECT *, SUM(is_start) OVER (ORDER BY timestamp) AS trip_num
    FROM gaps
),
haversine AS (
    SELECT *,
        6371 * 2 * ASIN(SQRT(
            POWER(SIN(RADIANS(latitude  - prev_lat) / 2), 2) +
            COS(RADIANS(prev_lat)) * COS(RADIANS(latitude)) *
            POWER(SIN(RADIANS(longitude - prev_lng) / 2), 2)
        )) AS segment_km
    FROM grouped
    WHERE prev_lat IS NOT NULL
),
trips AS (
    SELECT
        trip_num,
        MIN(timestamp) AS start_time,
        MAX(timestamp) AS end_time,
        SUM(segment_km) AS distance_km,
        epoch(MAX(timestamp) - MIN(timestamp)) / 60.0 AS duration_min,
        AVG(CASE WHEN speed > 2 THEN speed END) AS avg_speed,
        MAX(speed) AS max_speed
    FROM haversine
    GROUP BY trip_num
    HAVING MAX(speed) > 2 AND SUM(segment_km) > 0.1
)
SELECT
    COUNT(*)                                    AS total_trips,
    ROUND(COALESCE(SUM(distance_km), 0), 2)    AS total_km,
    ROUND(COALESCE(SUM(duration_min), 0) / 60.0, 1) AS total_hours,
    ROUND(AVG(avg_speed), 1)                   AS avg_speed,
    ROUND(MAX(max_speed), 1)                   AS max_speed
FROM trips
"""

LOCATIONS_SQL = """
SELECT id, device_id, plate, latitude, longitude, speed, status_name, timestamp
FROM locations
WHERE device_id = ?
  AND timestamp >= ?::TIMESTAMPTZ
  AND timestamp <= ?::TIMESTAMPTZ
ORDER BY timestamp ASC
LIMIT 10000
"""


def query_trips(device_id: str, days: int) -> list[dict]:
    with db() as conn:
        rows = conn.execute(TRIPS_SQL, [device_id, days]).fetchall()
        cols = ["trip_num", "start_time", "end_time", "distance_km",
                "duration_min", "avg_speed", "max_speed"]
        return [dict(zip(cols, row)) for row in rows]


def query_stats(device_id: str, days: int) -> dict[str, Any]:
    with db() as conn:
        row = conn.execute(STATS_SQL, [device_id, days]).fetchone()
        if row is None:
            return {"total_trips": 0, "total_km": 0, "total_hours": 0,
                    "avg_speed": None, "max_speed": None}
        cols = ["total_trips", "total_km", "total_hours", "avg_speed", "max_speed"]
        return dict(zip(cols, row))


def query_locations(device_id: str, from_ts: str, to_ts: str) -> list[dict]:
    with db() as conn:
        rows = conn.execute(LOCATIONS_SQL, [device_id, from_ts, to_ts]).fetchall()
        cols = ["id", "device_id", "plate", "latitude", "longitude",
                "speed", "status_name", "timestamp"]
        return [dict(zip(cols, row)) for row in rows]
