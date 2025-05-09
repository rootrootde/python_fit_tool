from datetime import datetime, timedelta, timezone
from typing import Optional

from fit_tool.base_type import BaseType
from fit_tool.data_message import DataMessage
from fit_tool.definition_message import DefinitionMessage
from fit_tool.developer_field import DeveloperField
from fit_tool.endian import Endian
from fit_tool.field import Field
from fit_tool.utils.conversions import to_degrees, to_semicircles


class WaypointMessage(DataMessage):
    ID = 29
    NAME = "waypoint"

    def __setattr__(self, key, value):
        # Bypass name property setter during DataMessage.__init__
        if key == "name" and "fields" not in self.__dict__:
            self.__dict__[key] = value
        else:
            super().__setattr__(key, value)

    @staticmethod
    def __get_field_size(definition_message: DefinitionMessage, field_id: int) -> int:
        size = 0
        if definition_message:
            field_definition = definition_message.get_field_definition(field_id)
            if field_definition:
                size = field_definition.size
        return size

    def __init__(
        self,
        definition_message: Optional[DefinitionMessage] = None,
        developer_fields: Optional[list[DeveloperField]] = None,
        local_id: int = 0,
        endian: Endian = Endian.LITTLE,
    ):
        super().__init__(
            global_id=WaypointMessage.ID,
            local_id=definition_message.local_id if definition_message else local_id,
            endian=definition_message.endian if definition_message else endian,
            definition_message=definition_message,
            developer_fields=developer_fields,
            fields=[
                MessageIndexField(
                    size=self.__get_field_size(
                        definition_message, MessageIndexField.ID
                    ),
                    growable=definition_message is None,
                ),
                NameField(
                    size=self.__get_field_size(definition_message, NameField.ID),
                    growable=definition_message is None,
                ),
                PositionLatField(
                    size=self.__get_field_size(definition_message, PositionLatField.ID),
                    growable=definition_message is None,
                ),
                PositionLongField(
                    size=self.__get_field_size(
                        definition_message, PositionLongField.ID
                    ),
                    growable=definition_message is None,
                ),
                WaypointSymbolField(
                    size=self.__get_field_size(
                        definition_message, WaypointSymbolField.ID
                    ),
                    growable=definition_message is None,
                ),
                AltitudeField(
                    size=self.__get_field_size(definition_message, AltitudeField.ID),
                    growable=definition_message is None,
                ),
                TimestampField(
                    size=self.__get_field_size(definition_message, TimestampField.ID),
                    growable=definition_message is None,
                ),
                WaypointDetailsField(
                    size=self.__get_field_size(
                        definition_message, WaypointDetailsField.ID
                    ),
                    growable=definition_message is None,
                ),
            ],
        )
        self.name = WaypointMessage.NAME
        self.growable = self.definition_message is None

    @property
    def message_index(self) -> Optional[int]:
        field = self.get_field(MessageIndexField.ID)
        return field.get_value() if field and field.is_valid() else None

    @message_index.setter
    def message_index(self, value: int):
        field = self.get_field(MessageIndexField.ID)
        if field:
            field.set_value(0, value) if value is not None else field.clear()

    @property
    def name(self) -> Optional[str]:
        field = self.get_field(NameField.ID)
        return field.get_value() if field and field.is_valid() else None

    @name.setter
    def name(self, value: str):
        field = self.get_field(NameField.ID)
        if field:
            if value is None:
                field.clear()
            else:
                field.set_value(0, value)

    @property
    def position_lat(self) -> Optional[float]:
        field = self.get_field(PositionLatField.ID)
        return to_degrees(field.get_value()) if field and field.is_valid() else None

    @position_lat.setter
    def position_lat(self, value: float):
        field = self.get_field(PositionLatField.ID)
        if field:
            field.set_value(
                0, to_semicircles(value)
            ) if value is not None else field.clear()

    @property
    def position_long(self) -> Optional[float]:
        field = self.get_field(PositionLongField.ID)
        return to_degrees(field.get_value()) if field and field.is_valid() else None

    @position_long.setter
    def position_long(self, value: float):
        field = self.get_field(PositionLongField.ID)
        if field:
            field.set_value(
                0, to_semicircles(value)
            ) if value is not None else field.clear()

    @property
    def waypoint_symbol(self) -> Optional[int]:
        field = self.get_field(WaypointSymbolField.ID)
        return field.get_value() if field and field.is_valid() else None

    @waypoint_symbol.setter
    def waypoint_symbol(self, value: int):
        field = self.get_field(WaypointSymbolField.ID)
        if field:
            field.set_value(0, value) if value is not None else field.clear()

    @property
    def altitude(self) -> Optional[float]:
        field = self.get_field(AltitudeField.ID)
        return field.get_value() if field and field.is_valid() else None

    @altitude.setter
    def altitude(self, value: float):
        field = self.get_field(AltitudeField.ID)
        if field:
            field.set_value(0, value) if value is not None else field.clear()

    @property
    def timestamp(self) -> Optional[datetime]:
        field = self.get_field(TimestampField.ID)
        if field and field.is_valid():
            return datetime(1989, 12, 31) + timedelta(seconds=field.get_value())
        return None

    @timestamp.setter
    def timestamp(self, value: datetime):
        field = self.get_field(TimestampField.ID)
        if field:
            if value is not None:
                delta = int(
                    (
                        value - datetime(1989, 12, 31, tzinfo=timezone.utc)
                    ).total_seconds()
                )
                field.set_value(0, delta)
            else:
                field.clear()

    @property
    def waypoint_details(self) -> Optional[str]:
        field = self.get_field(WaypointDetailsField.ID)
        return field.get_value() if field and field.is_valid() else None

    @waypoint_details.setter
    def waypoint_details(self, value: str):
        field = self.get_field(WaypointDetailsField.ID)
        if field:
            field.set_value(0, value) if value is not None else field.clear()


class NameField(Field):
    ID = 0

    def __init__(self, size: int = 0, growable: bool = True):
        super().__init__(
            name="name",
            field_id=self.ID,
            base_type=BaseType.STRING,
            size=size,
            growable=growable,
            sub_fields=[],
        )


class PositionLatField(Field):
    ID = 1

    def __init__(self, size: int = 0, growable: bool = True):
        super().__init__(
            name="position_lat",
            field_id=self.ID,
            base_type=BaseType.SINT32,
            size=size,
            growable=growable,
            sub_fields=[],
        )


class PositionLongField(Field):
    ID = 2

    def __init__(self, size: int = 0, growable: bool = True):
        super().__init__(
            name="position_long",
            field_id=self.ID,
            base_type=BaseType.SINT32,
            size=size,
            growable=growable,
            sub_fields=[],
        )


class WaypointSymbolField(Field):
    ID = 3

    def __init__(self, size: int = 0, growable: bool = True):
        super().__init__(
            name="waypoint_symbol",
            field_id=self.ID,
            base_type=BaseType.UINT16,
            size=size,
            growable=growable,
            sub_fields=[],
        )


class AltitudeField(Field):
    ID = 4

    def __init__(self, size: int = 0, growable: bool = True):
        super().__init__(
            name="altitude",
            field_id=self.ID,
            base_type=BaseType.UINT16,
            offset=2500,
            scale=5,
            units="m",
            size=size,
            growable=growable,
            sub_fields=[],
        )


class WaypointDetailsField(Field):
    ID = 6

    def __init__(self, size: int = 0, growable: bool = True):
        super().__init__(
            name="waypoint_details",
            field_id=self.ID,
            base_type=BaseType.STRING,
            size=size,
            growable=growable,
            sub_fields=[],
        )


class MessageIndexField(Field):
    ID = 254

    def __init__(self, size: int = 0, growable: bool = True):
        super().__init__(
            name="message_index",
            field_id=self.ID,
            base_type=BaseType.UINT16,
            offset=0,
            scale=1,
            size=size,
            growable=growable,
            sub_fields=[],
        )


class TimestampField(Field):
    ID = 253

    def __init__(self, size: int = 0, growable: bool = True):
        super().__init__(
            name="timestamp",
            field_id=self.ID,
            base_type=BaseType.UINT32,
            offset=0,
            scale=1,
            size=size,
            growable=growable,
            sub_fields=[],
        )
