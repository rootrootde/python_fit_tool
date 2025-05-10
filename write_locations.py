import argparse
from datetime import datetime, timezone

from fit_tool.fit_file_builder import FitFileBuilder
from fit_tool.profile.messages.file_creator_message import FileCreatorMessage
from fit_tool.profile.messages.file_id_message import FileIdMessage
from fit_tool.profile.messages.location_message import LocationMessage
from fit_tool.profile.messages.location_settings_message import LocationSettingsMessage
from fit_tool.profile.profile_type import (
    FileType,
    GarminProduct,
    LocationSettings,
    Manufacturer,
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
    fid.product = GarminProduct.EDGE_EXPLORE2
    fid.serial_number = 3504484629
    fid.time_created = get_timestamp_from_datetime(datetime.now())
    fid.number = 1
    fid.product_name = "Edge Explore 2"
    builder.add(fid)
    # File Creator
    fc = FileCreatorMessage()
    fc.software_version = 2618
    fc.hardware_version = 1
    builder.add(fc)
    return builder


def add_location_settings(builder: FitFileBuilder, setting):
    ws = LocationSettingsMessage()
    ws.location_settings = setting
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
    wp = LocationMessage()
    wp.location_name = name  # Corrected from wp.name
    wp.description = description  # Corrected from wp.waypoint_details
    wp.position_lat = lat
    wp.position_long = lon
    wp.altitude = alt
    wp.timestamp = 1746871377000
    wp.symbol = symbol  # Corrected from wp.waypoint_symbol
    wp.message_index = index
    builder.add(wp)


def create_example_fit_file(out_path: str):
    builder = build_base_builder()
    add_location_settings(builder, LocationSettings.REPLACE)

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
    parser.add_argument("-o", "--output", default="bla.fit", help="Output FIT filename")
    args = parser.parse_args()
    create_example_fit_file(args.output)
