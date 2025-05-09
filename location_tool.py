import argparse
from datetime import datetime, timezone

from fit_tool.fit_file_builder import FitFileBuilder
from fit_tool.profile.messages.file_creator_message import FileCreatorMessage
from fit_tool.profile.messages.file_id_message import FileIdMessage
from fit_tool.profile.messages.waypoint_message import WaypointMessage
from fit_tool.profile.messages.waypoint_settings_message import WaypointSettingsMessage
from fit_tool.profile.profile_type import (
    FileType,
    GarminProduct,
    Manufacturer,
    WaypointSettings,
)


def get_timestamp_from_datetime(dt: datetime) -> int:
    """Converts a datetime object to an integer timestamp."""
    return round(dt.timestamp()) * 1000


def build_base_builder() -> FitFileBuilder:
    builder = FitFileBuilder(auto_define=True, min_string_size=50)
    # File ID
    fid = FileIdMessage()
    fid.type = FileType.LOCATIONS
    fid.manufacturer = Manufacturer.GARMIN
    fid.product = GarminProduct.EDGE_EXPLORE_2
    fid.serial_number = 3504484629
    fid.time_created = get_timestamp_from_datetime(datetime.now())
    builder.add(fid)
    # File Creator
    fc = FileCreatorMessage()
    fc.software_version = 2618
    fc.hardware_version = 1
    builder.add(fc)
    return builder


def add_waypoint_settings(builder: FitFileBuilder, setting=WaypointSettings.REPLACE):
    ws = WaypointSettingsMessage()
    ws.waypoint_setting = setting
    builder.add(ws)


def add_waypoint(
    builder: FitFileBuilder,
    name: str,
    description: str,
    lat: float,
    lon: float,
    alt: float,
    symbol: int,
    index: int,
):
    wp = WaypointMessage()
    wp.name = name
    wp.waypoint_details = description
    wp.position_lat = lat
    wp.position_long = lon
    wp.altitude = alt
    wp.timestamp = datetime.now(timezone.utc)
    wp.waypoint_symbol = symbol
    wp.message_index = index
    builder.add(wp)


def create_example_fit_file(out_path: str):
    builder = build_base_builder()
    add_waypoint_settings(builder, WaypointSettings.REPLACE)

    waypoints = [
        ("Home Base", "Starting point", 51.2600, 7.1420, 150.0, 0),
        ("Checkpoint 1", "First waypoint", 51.2700, 7.1500, 160.0, 1),
        ("Checkpoint 2", "Second waypoint", 51.2800, 7.1600, 170.0, 2),
    ]

    for index, (name, description, lat, lon, alt, symbol) in enumerate(waypoints):
        add_waypoint(builder, name, description, lat, lon, alt, symbol, index)

    fit_file = builder.build()
    fit_file.to_file(out_path)
    print(f"✅ Written: {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a FIT file with example waypoints"
    )
    parser.add_argument(
        "-o", "--output", default="Locations.fit", help="Output FIT filename"
    )
    args = parser.parse_args()
    create_example_fit_file(args.output)
