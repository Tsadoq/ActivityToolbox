from lxml import etree, objectify


def parse_tcx_file(file_path: str) -> objectify.ObjectifiedElement:
    tree = objectify.parse(file_path)
    return tree.getroot()


def get_activity_from_tcx(
    tcx_file: objectify.ObjectifiedElement,
) -> objectify.ObjectifiedElement:
    return tcx_file.Activities.Activity


def get_track_from_activity(
    activity: objectify.ObjectifiedElement,
) -> objectify.ObjectifiedElement:
    print(activity.Lap.Track)
    return activity.Lap.Track


def get_total_distance(track: objectify.ObjectifiedElement) -> float:
    for point in reversed(track):
        nsmap = point.nsmap
        if point.find("DistanceMeters", nsmap) is not None:
            return float(point.DistanceMeters)
    print("No distance found")
    return 0.0


def increment_distance(
    track: objectify.ObjectifiedElement, percentage: float
) -> objectify.ObjectifiedElement:
    last_distance = 0.0
    original_last_distance = last_distance
    for point in track.Trackpoint:
        nsmap = point.nsmap
        if point.find("DistanceMeters", nsmap) is not None:
            distance = float(point.DistanceMeters)
            difference = distance - original_last_distance
            new_distance = last_distance + difference * (1 + percentage / 100)
            original_last_distance = distance
            point.DistanceMeters._setText(str(new_distance))
            last_distance = new_distance
    return track


if __name__ == "__main__":
    input_file = "/Users/tsadoq/Downloads/Corsa_pomeridiana-3.tcx"
    output_file = "/Users/tsadoq/Downloads/Corsa_pomeridiana-3_modified.tcx"

    root = parse_tcx_file(input_file)
    activity = get_activity_from_tcx(root)
    track = get_track_from_activity(activity)
    tot_distance = get_total_distance(track)
    objective_distance = 18_030.0
    delta = objective_distance - tot_distance
    print(f"Total distance: {tot_distance} meters")
    print(f"Objective distance: {objective_distance} meters")
    print(f"Delta increment: {delta} meters")
    print(f"Percentage increment: {delta / tot_distance * 100:.2f}%")
    increment_distance(track, delta / tot_distance * 100)
    new_tot_distance = get_total_distance(track)
    print(f"New total distance: {new_tot_distance} meters")

    # Save the modified XML
    objectify.deannotate(root)
    tree = etree.ElementTree(root)
    tree.write(output_file, xml_declaration=True, encoding="UTF-8", pretty_print=True)
    print(f"\nModified file saved to: {output_file}")

    # Sanity check: read the saved file and verify the distance
    print("\n--- Sanity Check ---")
    saved_root = parse_tcx_file(output_file)
    saved_activity = get_activity_from_tcx(saved_root)
    saved_track = get_track_from_activity(saved_activity)
    saved_distance = get_total_distance(saved_track)
    print(f"Distance from saved file: {saved_distance} meters")
    if abs(saved_distance - objective_distance) < 0.1:
        print("✓ Sanity check PASSED: Distance matches objective")
    else:
        print(
            f"✗ Sanity check FAILED: Expected {objective_distance}, got {saved_distance}"
        )
