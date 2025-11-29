"""Core SportActivity model."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List, Literal, Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from ..models.device import DeviceInfo
from ..models.lap import Lap
from ..models.trackpoint import TrackPoint
from ..types import Meters


class SportActivity(BaseModel):
    """
    Unified activity model spanning GPX / TCX / FIT.

    You can:
    - Load any file into this structure via a format-specific parser.
    - Run transformations purely on this model.
    - Export back to any format via writers that consume this model.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore",
        validate_assignment=True,
    )

    # High-level identifiers & provenance
    id: Optional[str] = Field(
        default=None,
        description="Optional application-level identifier for the activity.",
    )
    source_format: Optional[Literal["gpx", "tcx", "fit", "other"]] = Field(
        default=None,
        description="Format this activity was originally loaded from.",
    )

    sport_type: Optional[str] = Field(
        default=None,
        description="High-level sport type (e.g. 'Running', 'Cycling', 'Hiking').",
    )
    sport_subtype: Optional[str] = Field(
        default=None,
        description="Optional sub-sport or profile (e.g. 'Trail running', 'Indoor cycling').",
    )

    start_time: Optional[datetime] = Field(
        default=None,
        description="Start time of the activity; can be inferred from the first track point.",
    )

    total_distance: Optional[Meters] = Field(
        default=None,
        description="Total distance of the activity in meters (can be inferred).",
    )
    total_calories: Optional[float] = Field(
        default=None,
        description="Total calories burned over the entire activity.",
    )
    total_ascent: Optional[float] = Field(
        default=None,
        description="Total ascent over the entire activity in meters.",
    )
    total_descent: Optional[float] = Field(
        default=None,
        description="Total descent over the entire activity in meters.",
    )

    device_info: Optional[DeviceInfo] = Field(
        default=None,
        description="Information about the device or application that recorded the activity.",
    )

    laps: List[Lap] = Field(
        default_factory=list,
        description="List of laps/segments; may be empty or length=1 for non-lap formats.",
    )

    track_points: List[TrackPoint] = Field(
        default_factory=list,
        description="Flat time-ordered list of all track points in the activity.",
    )

    # ---------------------------- Validators & helpers -----------------------------

    @field_validator("track_points")
    @classmethod
    def _ensure_sorted_by_time(cls, v: List[TrackPoint]) -> List[TrackPoint]:
        """
        Ensure track points are sorted by timestamp.
        """
        return sorted(v, key=lambda tp: tp.timestamp)

    @model_validator(mode="after")
    def _derive_summary_fields(self) -> "SportActivity":
        """
        Derive start_time and total_distance if they were not explicitly provided.
        """
        # Derive start_time from first track point if missing
        if self.start_time is None and self.track_points:
            self.start_time = self.track_points[0].timestamp

        # Derive total_distance from the last point with distance if missing
        if self.total_distance is None and self.track_points:
            last_with_dist = next(
                (tp for tp in reversed(self.track_points) if tp.distance is not None),
                None,
            )
            if last_with_dist is not None:
                self.total_distance = last_with_dist.distance

        return self

    # ----------------------------- Computed fields --------------------------------

    @property
    def end_time(self) -> Optional[datetime]:
        """
        End time derived from the last track point.
        """
        if not self.track_points:
            return None
        return self.track_points[-1].timestamp

    @property
    def total_duration(self) -> Optional[timedelta]:
        """
        Total duration derived from start_time and end_time, if both are known.
        """
        if self.start_time is None or self.end_time is None:
            return None
        return self.end_time - self.start_time

    @property
    def has_gps(self) -> bool:
        """
        Whether the activity has at least one point with GPS coordinates.
        """
        return any(
            tp.latitude is not None and tp.longitude is not None
            for tp in self.track_points
        )

    @property
    def bounding_box(self) -> Optional[Dict[str, float]]:
        """
        Bounding box of all GPS points: {min_lat, max_lat, min_lon, max_lon}.
        Returns None if there are no GPS points.
        """
        lats = [tp.latitude for tp in self.track_points if tp.latitude is not None]
        lons = [tp.longitude for tp in self.track_points if tp.longitude is not None]
        if not lats or not lons:
            return None
        return {
            "min_lat": min(lats),
            "max_lat": max(lats),
            "min_lon": min(lons),
            "max_lon": max(lons),
        }

    def __str__(self) -> str:
        """Pretty print sport activity information."""
        lines = ["=" * 60]
        lines.append("SPORT ACTIVITY")
        lines.append("=" * 60)

        if self.id:
            lines.append(f"ID: {self.id}")

        if self.sport_type:
            sport_str = self.sport_type
            if self.sport_subtype:
                sport_str += f" ({self.sport_subtype})"
            lines.append(f"Sport: {sport_str}")

        if self.source_format:
            lines.append(f"Source Format: {self.source_format.upper()}")

        lines.append("")
        lines.append("Time & Duration:")
        lines.append("-" * 60)

        if self.start_time:
            lines.append(f"  Start: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")

        if self.end_time:
            lines.append(f"  End: {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}")

        if self.total_duration:
            total_secs = int(self.total_duration.total_seconds())
            hours, remainder = divmod(total_secs, 3600)
            minutes, seconds = divmod(remainder, 60)
            if hours > 0:
                lines.append(f"  Duration: {hours}h {minutes}m {seconds}s")
            elif minutes > 0:
                lines.append(f"  Duration: {minutes}m {seconds}s")
            else:
                lines.append(f"  Duration: {seconds}s")

        lines.append("")
        lines.append("Summary:")
        lines.append("-" * 60)

        if self.total_distance is not None:
            if self.total_distance >= 1000:
                lines.append(f"  Distance: {self.total_distance / 1000:.2f}km")
            else:
                lines.append(f"  Distance: {self.total_distance:.1f}m")

        if self.total_calories is not None:
            lines.append(f"  Calories: {self.total_calories:.0f}kcal")

        if self.total_ascent is not None:
            lines.append(f"  Total Ascent: {self.total_ascent:.1f}m")

        if self.total_descent is not None:
            lines.append(f"  Total Descent: {self.total_descent:.1f}m")

        lines.append(f"  GPS Data: {'Yes' if self.has_gps else 'No'}")

        if self.bounding_box:
            bbox = self.bounding_box
            lines.append(
                f"  Bounding Box: ({bbox['min_lat']:.6f}, {bbox['min_lon']:.6f}) to ({bbox['max_lat']:.6f}, {bbox['max_lon']:.6f})"
            )

        lines.append("")
        lines.append("Data Points:")
        lines.append("-" * 60)
        lines.append(f"  Track Points: {len(self.track_points)}")
        lines.append(f"  Laps: {len(self.laps)}")

        if self.device_info:
            lines.append("")
            lines.append("Device Information:")
            lines.append("-" * 60)
            if self.device_info.device_name:
                lines.append(f"  Device: {self.device_info.device_name}")
            if self.device_info.manufacturer:
                lines.append(f"  Manufacturer: {self.device_info.manufacturer}")
            if self.device_info.product_id:
                lines.append(f"  Product ID: {self.device_info.product_id}")
            if self.device_info.firmware_version:
                lines.append(f"  Firmware: {self.device_info.firmware_version}")

        lines.append("=" * 60)

        return "\n".join(lines)


__all__ = ["SportActivity"]
