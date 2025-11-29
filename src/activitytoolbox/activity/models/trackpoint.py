"""Track point model for time-series activity data."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ..types import BPM, RPM, Celsius, Latitude, Longitude, Meters, SpeedMS, Watts


class TrackPoint(BaseModel):
    """
    Single time-series sample in the activity (GPS + sensors).
    Matches the superset of GPX/TCX/FIT per-point fields.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore",
        validate_assignment=True,
    )

    timestamp: datetime = Field(
        description="Timestamp of this sample in UTC (or source-local if not normalized).",
    )

    latitude: Optional[Latitude] = Field(
        default=None,
        description="Latitude in decimal degrees; None for non-GPS samples (e.g. trainer).",
    )
    longitude: Optional[Longitude] = Field(
        default=None,
        description="Longitude in decimal degrees; None for non-GPS samples.",
    )
    elevation: Optional[float] = Field(
        default=None,
        description="Elevation/altitude in meters above sea level, if available.",
    )

    distance: Optional[Meters] = Field(
        default=None,
        description=(
            "Cumulative distance in meters from start to this sample. "
            "Absent in some GPX files; often present in TCX/FIT."
        ),
    )
    speed: Optional[SpeedMS] = Field(
        default=None,
        description="Instantaneous speed at this point in m/s, if recorded.",
    )

    heart_rate: Optional[BPM] = Field(
        default=None,
        description="Heart rate in beats per minute.",
    )
    cadence: Optional[RPM] = Field(
        default=None,
        description="Cadence in revolutions per minute (running or cycling).",
    )
    power: Optional[Watts] = Field(
        default=None,
        description="Power in watts, typically for cycling; from FIT/TCX extensions.",
    )
    temperature: Optional[Celsius] = Field(
        default=None,
        description="Ambient or skin temperature in °C if available.",
    )

    source_index: Optional[int] = Field(
        default=None,
        description="Index of this point in the original file (for round-tripping/debug).",
    )

    extensions: Dict[str, Any] = Field(
        default_factory=dict,
        description="Free-form dictionary for format-specific or unknown extra fields.",
    )

    @model_validator(mode="after")
    def _validate_gps_pair(self) -> "TrackPoint":
        """
        Ensure latitude and longitude are either both present or both None,
        which simplifies downstream handling.
        """
        if (self.latitude is None) ^ (self.longitude is None):
            raise ValueError("latitude and longitude must be both set or both None")
        return self


__all__ = ["TrackPoint"]
