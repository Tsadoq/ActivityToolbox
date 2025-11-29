"""TCX Loader"""

from datetime import datetime, timedelta
from typing import Optional

from lxml import objectify

from .. import SportActivity
from ..models import DeviceInfo, Lap, TrackPoint


def load_tcx(file_path: str) -> Optional[SportActivity]:
    """Load an activity from a TCX file."""
    tree = objectify.parse(file_path)
    root = tree.getroot()

    # Remove namespace prefix for easier access
    objectify.deannotate(root, cleanup_namespaces=True)

    nsmap = root.nsmap

    # Navigate to Activities
    activities = root.find("Activities", nsmap)
    if activities is None:
        return None

    activity = activities.find("Activity", nsmap)
    if activity is None:
        return None

    # Extract sport type (attribute in TCX)
    sport_type = activity.get("Sport")

    # Parse laps
    laps = []
    track_points = []
    global_index = 0

    for lap_idx, lap_elem in enumerate(activity.findall("Lap", nsmap)):
        lap_start = datetime.fromisoformat(
            lap_elem.get("StartTime").replace("Z", "+00:00")
        )

        # Track start index for this lap
        lap_start_index = global_index

        # Parse track points within this lap
        for track in lap_elem.findall("Track", nsmap):
            for tp_elem in track.findall("Trackpoint", nsmap):
                # Extract position if available
                lat = None
                lon = None
                position = tp_elem.find("Position", nsmap)
                if position is not None:
                    lat_elem = position.find("LatitudeDegrees", nsmap)
                    lon_elem = position.find("LongitudeDegrees", nsmap)
                    if lat_elem is not None:
                        lat = float(lat_elem)
                    if lon_elem is not None:
                        lon = float(lon_elem)

                # Extract heart rate if available
                hr = None
                hr_bpm = tp_elem.find("HeartRateBpm", nsmap)
                if hr_bpm is not None:
                    hr_value = hr_bpm.find("Value", nsmap)
                    if hr_value is not None:
                        hr = int(hr_value)

                # Extract other trackpoint fields
                time_elem = tp_elem.find("Time", nsmap)
                altitude_elem = tp_elem.find("AltitudeMeters", nsmap)
                distance_elem = tp_elem.find("DistanceMeters", nsmap)
                cadence_elem = tp_elem.find("Cadence", nsmap)

                tp = TrackPoint(
                    timestamp=datetime.fromisoformat(
                        str(time_elem).replace("Z", "+00:00")
                    ),
                    latitude=lat,
                    longitude=lon,
                    elevation=float(altitude_elem)
                    if altitude_elem is not None
                    else None,
                    distance=float(distance_elem)
                    if distance_elem is not None
                    else None,
                    heart_rate=hr,
                    cadence=int(cadence_elem) if cadence_elem is not None else None,
                    source_index=global_index,
                )
                track_points.append(tp)
                global_index += 1

        # Extract lap summary data
        total_time_elem = lap_elem.find("TotalTimeSeconds", nsmap)
        distance_meters_elem = lap_elem.find("DistanceMeters", nsmap)
        max_speed_elem = lap_elem.find("MaximumSpeed", nsmap)
        calories_elem = lap_elem.find("Calories", nsmap)
        intensity_elem = lap_elem.find("Intensity", nsmap)
        trigger_elem = lap_elem.find("TriggerMethod", nsmap)
        cadence_elem = lap_elem.find("Cadence", nsmap)

        # Average and max heart rate
        avg_hr = None
        avg_hr_bpm = lap_elem.find("AverageHeartRateBpm", nsmap)
        if avg_hr_bpm is not None:
            avg_hr_value = avg_hr_bpm.find("Value", nsmap)
            if avg_hr_value is not None:
                avg_hr = int(avg_hr_value)

        max_hr = None
        max_hr_bpm = lap_elem.find("MaximumHeartRateBpm", nsmap)
        if max_hr_bpm is not None:
            max_hr_value = max_hr_bpm.find("Value", nsmap)
            if max_hr_value is not None:
                max_hr = int(max_hr_value)

        lap = Lap(
            index=lap_idx,
            start_time=lap_start,
            total_time=_parse_timedelta(total_time_elem)
            if total_time_elem is not None
            else None,
            total_distance=float(distance_meters_elem)
            if distance_meters_elem is not None
            else None,
            max_speed=float(max_speed_elem) if max_speed_elem is not None else None,
            total_calories=float(calories_elem) if calories_elem is not None else None,
            avg_heart_rate=avg_hr,
            max_heart_rate=max_hr,
            avg_cadence=int(cadence_elem) if cadence_elem is not None else None,
            intensity=str(intensity_elem) if intensity_elem is not None else None,
            trigger=str(trigger_elem) if trigger_elem is not None else None,
            start_index=lap_start_index,
            end_index=global_index - 1 if global_index > 0 else None,
        )
        laps.append(lap)

    # Extract device info if present
    device_info = None
    creator = activity.find("Creator", nsmap)
    if creator is not None:
        name_elem = creator.find("Name", nsmap)
        product_id_elem = creator.find("ProductID", nsmap)

        # Build firmware version string if version info is available
        firmware = None
        version = creator.find("Version", nsmap)
        if version is not None:
            major_elem = version.find("VersionMajor", nsmap)
            minor_elem = version.find("VersionMinor", nsmap)
            if major_elem is not None and minor_elem is not None:
                firmware = f"{major_elem}.{minor_elem}"
            elif major_elem is not None:
                firmware = str(major_elem)

        device_info = DeviceInfo(
            device_name=str(name_elem) if name_elem is not None else None,
            product_id=str(product_id_elem) if product_id_elem is not None else None,
            firmware_version=firmware,
        )

    return SportActivity(
        source_format="tcx",
        sport_type=sport_type,
        device_info=device_info,
        laps=laps,
        track_points=track_points,
    )


def _parse_timedelta(seconds_elem) -> timedelta:
    """Parse TCX TotalTimeSeconds element into timedelta."""
    return timedelta(seconds=float(seconds_elem))
