"""Lap model for activity segments."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, computed_field

from ..types import BPM, RPM, Meters, SpeedMS, Watts


class Lap(BaseModel):
    """
    Logical segment of an activity (lap/interval), with summary stats.
    TCX/FIT map directly; GPX can use a single synthetic lap if needed.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore",
        validate_assignment=True,
    )

    index: Optional[int] = Field(
        default=None,
        description="0-based lap index in the original source, if known.",
    )

    start_time: datetime = Field(
        description="Start time of this lap.",
    )
    total_time: Optional[timedelta] = Field(
        default=None,
        description="Duration of the lap. If None, can be derived from track points.",
    )

    total_distance: Optional[Meters] = Field(
        default=None,
        description="Total distance of this lap in meters.",
    )

    max_speed: Optional[SpeedMS] = Field(
        default=None,
        description="Maximum speed during the lap in m/s.",
    )
    avg_speed: Optional[SpeedMS] = Field(
        default=None,
        description="Average speed during the lap in m/s.",
    )

    total_calories: Optional[float] = Field(
        default=None,
        description="Total calories burned during this lap.",
    )

    avg_heart_rate: Optional[BPM] = Field(
        default=None,
        description="Average heart rate in bpm.",
    )
    max_heart_rate: Optional[BPM] = Field(
        default=None,
        description="Maximum heart rate in bpm.",
    )

    avg_cadence: Optional[RPM] = Field(
        default=None,
        description="Average cadence in RPM.",
    )
    max_cadence: Optional[RPM] = Field(
        default=None,
        description="Maximum cadence in RPM.",
    )

    avg_power: Optional[Watts] = Field(
        default=None,
        description="Average power in watts.",
    )
    max_power: Optional[Watts] = Field(
        default=None,
        description="Maximum power in watts.",
    )

    total_ascent: Optional[float] = Field(
        default=None,
        description="Total positive elevation gain in meters.",
    )
    total_descent: Optional[float] = Field(
        default=None,
        description="Total negative elevation in meters.",
    )

    intensity: Optional[str] = Field(
        default=None,
        description="Intensity label (e.g. 'Active', 'Resting'), if provided.",
    )
    trigger: Optional[str] = Field(
        default=None,
        description="How the lap was triggered (e.g. 'Manual', 'Distance', 'Time').",
    )

    # Optional metadata for linking to track points
    start_index: Optional[int] = Field(
        default=None,
        description="Index into the global track_points list where this lap starts.",
    )
    end_index: Optional[int] = Field(
        default=None,
        description="Index into the global track_points list where this lap ends (inclusive).",
    )

    @computed_field
    @property
    def end_time(self) -> Optional[datetime]:
        """
        End time derived from start_time + total_time, if total_time is known.
        """
        if self.total_time is None:
            return None
        return self.start_time + self.total_time

    def __str__(self) -> str:
        """Pretty print lap information."""
        parts = []

        if self.index is not None:
            parts.append(f"Lap #{self.index + 1}")
        else:
            parts.append("Lap")

        parts.append(f"Start: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")

        if self.total_time is not None:
            total_secs = int(self.total_time.total_seconds())
            hours, remainder = divmod(total_secs, 3600)
            minutes, seconds = divmod(remainder, 60)
            if hours > 0:
                parts.append(f"Duration: {hours}h {minutes}m {seconds}s")
            elif minutes > 0:
                parts.append(f"Duration: {minutes}m {seconds}s")
            else:
                parts.append(f"Duration: {seconds}s")

        if self.total_distance is not None:
            if self.total_distance >= 1000:
                parts.append(f"Distance: {self.total_distance / 1000:.2f}km")
            else:
                parts.append(f"Distance: {self.total_distance:.1f}m")

        if self.avg_speed is not None:
            parts.append(
                f"Avg Speed: {self.avg_speed:.2f}m/s ({self.avg_speed * 3.6:.1f}km/h)"
            )

        if self.max_speed is not None:
            parts.append(
                f"Max Speed: {self.max_speed:.2f}m/s ({self.max_speed * 3.6:.1f}km/h)"
            )

        if self.avg_heart_rate is not None:
            parts.append(f"Avg HR: {self.avg_heart_rate}bpm")

        if self.max_heart_rate is not None:
            parts.append(f"Max HR: {self.max_heart_rate}bpm")

        if self.avg_cadence is not None:
            parts.append(f"Avg Cadence: {self.avg_cadence}rpm")

        if self.max_cadence is not None:
            parts.append(f"Max Cadence: {self.max_cadence}rpm")

        if self.avg_power is not None:
            parts.append(f"Avg Power: {self.avg_power}W")

        if self.max_power is not None:
            parts.append(f"Max Power: {self.max_power}W")

        if self.total_calories is not None:
            parts.append(f"Calories: {self.total_calories:.0f}kcal")

        if self.total_ascent is not None:
            parts.append(f"Ascent: {self.total_ascent:.1f}m")

        if self.total_descent is not None:
            parts.append(f"Descent: {self.total_descent:.1f}m")

        if self.intensity:
            parts.append(f"Intensity: {self.intensity}")

        if self.trigger:
            parts.append(f"Trigger: {self.trigger}")

        return "Lap(\n  " + "\n  ".join(parts) + "\n)"


__all__ = ["Lap"]
