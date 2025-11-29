"""Activity tracking and analysis module.

This module provides a unified data model for sport activities
across multiple formats (GPX, TCX, FIT).
"""

from .core import SportActivity
from .models import DeviceInfo, Lap, TrackPoint
from .types import (
    BPM,
    RPM,
    Celsius,
    Latitude,
    Longitude,
    Meters,
    Seconds,
    SpeedMS,
    Watts,
)

__all__ = [
    # Core models
    "SportActivity",
    # Component models
    "DeviceInfo",
    "Lap",
    "TrackPoint",
    # Type aliases
    "BPM",
    "RPM",
    "Celsius",
    "Latitude",
    "Longitude",
    "Meters",
    "Seconds",
    "SpeedMS",
    "Watts",
]
