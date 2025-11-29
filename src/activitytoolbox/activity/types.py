"""Type aliases with constraints for activity data."""

from typing import Annotated

from pydantic import Field

# ---- Type aliases with constraints -------------------------------------------------

Latitude = Annotated[float, Field(ge=-90.0, le=90.0)]
Longitude = Annotated[float, Field(ge=-180.0, le=180.0)]
Meters = Annotated[float, Field(ge=0.0)]
Seconds = Annotated[float, Field(ge=0.0)]
SpeedMS = Annotated[float, Field(ge=0.0)]
BPM = Annotated[int, Field(ge=0)]
RPM = Annotated[int, Field(ge=0)]
Watts = Annotated[int, Field(ge=0)]
Celsius = float

__all__ = [
    "Latitude",
    "Longitude",
    "Meters",
    "Seconds",
    "SpeedMS",
    "BPM",
    "RPM",
    "Watts",
    "Celsius",
]
