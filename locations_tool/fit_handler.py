from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

from fit_tool.data_message import DataMessage
from fit_tool.fit_file import FitFile
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


# --- Data Classes ---
@dataclass
class FitHeaderData:
    file_type: Optional[FileType] = None
    manufacturer: Optional[Manufacturer] = None
    product: Optional[GarminProduct] = (
        None  # This might be an int, map to GarminProduct enum if possible
    )
    serial_number: Optional[int] = None
    time_created: Optional[datetime] = None  # fit_tool might convert this automatically
    product_name: Optional[str] = None  # From FileIdMessage.product_name if available


@dataclass
class FitCreatorData:
    software_version: Optional[int] = None
    hardware_version: Optional[int] = None


@dataclass
class FitLocationSettingData:  # Renamed from FitWaypointSettingData
    waypoint_setting: Optional[LocationSettings] = None


@dataclass
class FitLocationData:  # Renamed from FitWaypointData
    name: Optional[str] = None
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude: Optional[float] = None
    timestamp: Optional[datetime] = None  # fit_tool might convert this automatically
    symbol: Optional[int] = None
    message_index: Optional[int] = None


@dataclass
class LocationsFitFileData:
    header: Optional[FitHeaderData] = None
    creator: Optional[FitCreatorData] = None
    settings: Optional[FitLocationSettingData] = None  # Updated type
    waypoints: List[FitLocationData] = field(default_factory=list)  # Updated type
    errors: List[str] = field(default_factory=list)


# --- Read Logic ---
def read_fit_file(file_path: str) -> LocationsFitFileData:
    fit_data = LocationsFitFileData()

    try:
        fit_file = FitFile.from_file(file_path)
    except Exception as e:
        fit_data.errors.append(f"Error opening or parsing FIT file: {e}")
        return fit_data

    for record_wrapper in fit_file.records:
        actual_message = record_wrapper.message

        if not isinstance(actual_message, DataMessage):
            continue

        definition_for_data = actual_message.definition_message
        global_id = definition_for_data.global_id

        try:
            if global_id == FileIdMessage.ID:
                msg = actual_message

                file_type_val = getattr(msg, "type", None)
                file_type_enum = None
                if file_type_val is not None:
                    try:
                        file_type_enum = FileType(file_type_val)
                    except ValueError:
                        fit_data.errors.append(
                            f"Invalid FileType value encountered: {file_type_val}"
                        )

                manufacturer_val = getattr(msg, "manufacturer", None)
                manufacturer_enum = None
                if manufacturer_val is not None:
                    try:
                        manufacturer_enum = Manufacturer(manufacturer_val)
                    except ValueError:
                        fit_data.errors.append(
                            f"Invalid Manufacturer value encountered: {manufacturer_val}"
                        )

                product_id_val = getattr(msg, "product", None)
                garmin_product_enum = None
                if (
                    manufacturer_enum == Manufacturer.GARMIN
                    and product_id_val is not None
                ):
                    try:
                        garmin_product_enum = GarminProduct(product_id_val)
                    except ValueError:
                        fit_data.errors.append(
                            f"Invalid GarminProduct value for manufacturer GARMIN: {product_id_val}"
                        )
                elif (
                    product_id_val is not None
                    and manufacturer_enum != Manufacturer.GARMIN
                ):
                    pass

                time_created_val = getattr(msg, "time_created", None)
                processed_time_created = None
                if isinstance(time_created_val, (int, float)):
                    try:
                        # Assuming time_created_val is milliseconds since Unix epoch based on field def
                        processed_time_created = datetime.fromtimestamp(
                            time_created_val / 1000.0, tz=timezone.utc
                        )
                    except Exception as e:
                        fit_data.errors.append(
                            f"Error converting FileIdMessage.time_created ({time_created_val}) to datetime: {e}"
                        )
                elif isinstance(time_created_val, datetime):
                    processed_time_created = (
                        time_created_val  # Already a datetime object
                    )
                elif time_created_val is not None:
                    fit_data.errors.append(
                        f"Unexpected type for FileIdMessage.time_created: {type(time_created_val)}. Value: {time_created_val}"
                    )

                fit_data.header = FitHeaderData(
                    file_type=file_type_enum,
                    manufacturer=manufacturer_enum,
                    product=garmin_product_enum,
                    serial_number=getattr(msg, "serial_number", None),
                    time_created=processed_time_created,  # Store datetime object
                    product_name=getattr(msg, "product_name", None),
                )
            elif global_id == FileCreatorMessage.ID:
                msg = actual_message
                fit_data.creator = FitCreatorData(
                    software_version=getattr(msg, "software_version", None),
                    hardware_version=getattr(msg, "hardware_version", None),
                )
            elif global_id == LocationSettingsMessage.ID:
                msg = actual_message
                setting_val = getattr(
                    msg, "location_settings", None
                )  # Changed to plural
                setting_enum = None
                if setting_val is not None:
                    try:
                        setting_enum = LocationSettings(setting_val)
                    except ValueError:
                        fit_data.errors.append(
                            f"Invalid LocationSetting value encountered: {setting_val}"
                        )
                fit_data.settings = FitLocationSettingData(  # Updated instantiation
                    waypoint_setting=setting_enum
                )
            elif global_id == LocationMessage.ID:
                msg = actual_message
                # msg.position_lat and msg.position_long from LocationMessage already return degrees
                lat_degrees = getattr(msg, "position_lat", None)
                lon_degrees = getattr(msg, "position_long", None)

                # Process timestamp from LocationMessage
                # Assuming msg.timestamp (from autogenerated LocationMessage) returns int: ms since Unix epoch
                raw_location_timestamp = getattr(msg, "timestamp", None)
                location_datetime_object = None
                if isinstance(raw_location_timestamp, (int, float)):
                    try:
                        location_datetime_object = datetime.fromtimestamp(
                            raw_location_timestamp / 1000.0, tz=timezone.utc
                        )
                    except Exception as e:
                        fit_data.errors.append(
                            f"Error converting LocationMessage.timestamp ({raw_location_timestamp}) to datetime: {e}"
                        )
                elif isinstance(
                    raw_location_timestamp, datetime
                ):  # Should ideally not happen if property returns int
                    location_datetime_object = raw_location_timestamp
                    if location_datetime_object.tzinfo is None:  # Ensure it's aware
                        location_datetime_object = location_datetime_object.replace(
                            tzinfo=timezone.utc
                        )
                    else:
                        location_datetime_object = location_datetime_object.astimezone(
                            timezone.utc
                        )
                elif raw_location_timestamp is not None:
                    fit_data.errors.append(
                        f"Unexpected type for LocationMessage.timestamp: {type(raw_location_timestamp)}. Value: {raw_location_timestamp}"
                    )

                waypoint = FitLocationData(  # Updated instantiation
                    name=getattr(
                        msg, "location_name", None
                    ),  # Corrected: use location_name
                    description=getattr(
                        msg, "description", None
                    ),  # Corrected: use description
                    latitude=lat_degrees,
                    longitude=lon_degrees,
                    altitude=getattr(msg, "altitude", None),
                    timestamp=location_datetime_object,  # Store processed datetime
                    symbol=getattr(msg, "symbol", None),  # Corrected: use symbol
                    message_index=getattr(msg, "message_index", None),
                )
                fit_data.waypoints.append(waypoint)
        except AttributeError as e:
            fit_data.errors.append(
                f"Attribute error processing message {type(actual_message).__name__} (ID: {global_id}): {e}"
            )
        except Exception as e:
            fit_data.errors.append(
                f"Unexpected error processing message {type(actual_message).__name__} (ID: {global_id}): {e}"
            )

    return fit_data


# --- Write Logic ---
def get_timestamp_from_datetime(dt: Optional[datetime]) -> Optional[int]:
    """Converts an optional datetime object to an integer timestamp in milliseconds since UTC epoch."""
    if dt is None:
        return None
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return round(dt.timestamp() * 1000)


def degrees_to_semicircles(degrees: Optional[float]) -> Optional[int]:
    """Converts degrees to semicircles."""
    if degrees is None:
        return None
    return round(degrees * (2**31 / 180.0))


def write_fit_file(file_path: str, fit_data: LocationsFitFileData) -> List[str]:
    """Writes the provided LocationsFitFileData to a .fit file."""
    errors: List[str] = []
    builder = FitFileBuilder(auto_define=True, min_string_size=50)

    # File ID Message - FIT files generally require a File ID.
    if fit_data.header:
        fid_msg = FileIdMessage()  # Changed variable name to avoid conflict
        header = fit_data.header
        if header.file_type is not None:
            fid_msg.type = header.file_type
        if header.manufacturer is not None:
            fid_msg.manufacturer = header.manufacturer
        if header.product is not None:
            # Product ID is just an int if not Garmin, GarminProduct enum otherwise
            if isinstance(header.product, GarminProduct):
                fid_msg.product = (
                    header.product.value
                )  # Use enum value for GarminProduct
            else:  # Assuming it's an int or None for non-Garmin or if not mapped
                fid_msg.product = header.product
        if header.serial_number is not None:
            fid_msg.serial_number = header.serial_number

        # The FileIdMessage.time_created setter expects a datetime object.
        # get_timestamp_from_datetime was for the old integer-based property.
        # If header.time_created is None, the property setter in FileIdMessage might handle it or use a default.
        # For safety, provide a default if None.
        fid_msg.time_created = header.time_created or datetime.now(timezone.utc)

        if header.product_name is not None:
            fid_msg.product_name = header.product_name
        builder.add(fid_msg)
    else:
        # Create a minimal valid FileIdMessage if none was provided from loaded data or user input
        fid_msg = FileIdMessage()
        fid_msg.type = FileType.LOCATION  # Default to LOCATION as per previous logic
        fid_msg.serial_number = 0
        builder.add(fid_msg)
        errors.append(
            "Warning: File ID data was missing or incomplete; a default File ID message was created."
        )

    # File Creator Message (Optional)
    if fit_data.creator:
        creator_msg = FileCreatorMessage()
        creator = fit_data.creator
        if creator.software_version is not None:
            creator_msg.software_version = creator.software_version
        if creator.hardware_version is not None:
            creator_msg.hardware_version = creator.hardware_version
        builder.add(creator_msg)

    # Location Settings Message (Optional but often needed by devices)
    if fit_data.settings and fit_data.settings.waypoint_setting is not None:
        ls_msg = LocationSettingsMessage()
        ls_msg.location_settings = fit_data.settings.waypoint_setting
        builder.add(ls_msg)
    else:
        # Always add a default LocationSettingsMessage if not present or not set
        ls_msg = LocationSettingsMessage()
        try:
            default_setting = LocationSettings.ADD
            ls_msg.location_settings = default_setting
        except ValueError:
            # Fallback if 0 is not a valid enum member, this indicates profile_type.py is not correctly defined
            # This part should ideally not be reached if LocationSettings enum is correctly populated.
            errors.append(
                "Critical Error: LocationSettings enum in profile_type.py is not correctly defined or is empty. Cannot set a default location setting."
            )
            # Do not add ls_msg if we can't set a valid default, or the FIT file might be invalid.
            # However, for locations.fit, it's often crucial.
            # For now, we'll log an error and proceed without it if the enum is broken.
            pass  # Or handle more gracefully, e.g. by not adding this message if no valid default
        if (
            not errors or "Critical Error" not in errors[-1]
        ):  # Only add if no critical error setting default
            builder.add(ls_msg)
        if not (fit_data.settings and fit_data.settings.waypoint_setting is not None):
            errors.append(
                "Warning: Location Settings data was missing or incomplete; a default setting was applied or attempted."
            )

    # Location Messages (Waypoints)
    for index, wp_data in enumerate(fit_data.waypoints):
        loc_msg = LocationMessage()
        if wp_data.name is not None:
            loc_msg.location_name = wp_data.name
        if wp_data.description is not None:
            loc_msg.description = wp_data.description
        if wp_data.latitude is not None:
            loc_msg.position_lat = wp_data.latitude
        if wp_data.longitude is not None:
            loc_msg.position_long = wp_data.longitude
        if wp_data.altitude is not None:
            loc_msg.altitude = wp_data.altitude
        if wp_data.timestamp is not None:
            loc_msg.timestamp = wp_data.timestamp
        if wp_data.symbol is not None:
            loc_msg.symbol = wp_data.symbol
        if wp_data.message_index is not None:
            loc_msg.message_index = wp_data.message_index
        builder.add(loc_msg)

    try:
        fit_file_built = builder.build()  # Call build() without arguments
        fit_file_built.to_file(file_path)  # Then call to_file() on the result
    except Exception as e:
        errors.append(f"Error building or writing FIT file: {e}")

    return errors
