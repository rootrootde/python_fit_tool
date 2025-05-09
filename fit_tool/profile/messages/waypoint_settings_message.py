from typing import Optional

from fit_tool.base_type import BaseType
from fit_tool.data_message import DataMessage
from fit_tool.definition_message import DefinitionMessage
from fit_tool.developer_field import DeveloperField
from fit_tool.endian import Endian
from fit_tool.field import Field


class WaypointSettingsMessage(DataMessage):
    ID = 189
    NAME = "waypoint_settings"

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
            global_id=WaypointSettingsMessage.ID,
            local_id=definition_message.local_id if definition_message else local_id,
            endian=definition_message.endian if definition_message else endian,
            name=WaypointSettingsMessage.NAME,
            definition_message=definition_message,
            developer_fields=developer_fields,
            fields=[
                WaypointSettingField(
                    size=self.__get_field_size(
                        definition_message, WaypointSettingField.ID
                    ),
                    growable=definition_message is None,
                )
            ],
        )
        self.growable = self.definition_message is None

    @property
    def waypoint_setting(self) -> Optional[int]:
        field = self.get_field(WaypointSettingField.ID)
        if field and field.is_valid():
            sub_field = field.get_valid_sub_field(self.fields)
            return field.get_value(sub_field=sub_field)
        return None

    @waypoint_setting.setter
    def waypoint_setting(self, value: int):
        field = self.get_field(WaypointSettingField.ID)
        if field:
            if value is None:
                field.clear()
            else:
                sub_field = field.get_valid_sub_field(self.fields)
                field.set_value(0, value, sub_field)


class WaypointSettingField(Field):
    ID = 0

    def __init__(self, size: int = 0, growable: bool = True):
        super().__init__(
            name="waypoint_setting",
            field_id=self.ID,
            base_type=BaseType.UINT8,
            offset=0,
            scale=1,
            size=size,
            growable=growable,
            sub_fields=[],
        )
