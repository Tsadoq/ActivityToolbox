"""Device information model."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class DeviceInfo(BaseModel):
    """
    Metadata about the device or app that recorded the activity.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore",
        validate_assignment=True,
    )

    device_name: Optional[str] = Field(
        default=None,
        description="Name of the device or application (e.g. 'Garmin Forerunner 945').",
    )
    manufacturer: Optional[str] = Field(
        default=None,
        description="Manufacturer of the device (e.g. 'Garmin').",
    )
    product_id: Optional[str] = Field(
        default=None,
        description="Product identifier or model number as reported by the source.",
    )
    firmware_version: Optional[str] = Field(
        default=None,
        description="Firmware or software version of the recording device/app.",
    )


__all__ = ["DeviceInfo"]
