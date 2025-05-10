import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from datetime import datetime, timezone

from PySide6.QtCore import QDateTime, Qt, Slot
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QComboBox,
    QDateTimeEdit,
    QDoubleSpinBox,
    QFileDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidgetItem,
)

import locations_tool.fit_handler as fit_handler
from fit_tool.profile.profile_type import FileType, GarminProduct, Manufacturer
from fit_tool.profile.profile_type import LocationSettings as FitLocationSettingsEnum
from locations_tool.gui.ui_main_window import Ui_MainWindow

FIELD_NAME_TO_HEADER_MAP = {
    "file_type": "File Type",
    "manufacturer": "Manufacturer",
    "product": "Product",
    "serial_number": "Serial Number",
    "time_created": "Time Created",
    "product_name": "Product Name",
    "software_version": "Software Version",
    "hardware_version": "Hardware Version",
    "waypoint_setting": "Location Setting",
    "name": "Name",
    "description": "Description",
    "latitude": "Latitude",
    "longitude": "Longitude",
    "altitude": "Altitude",
    "timestamp": "Timestamp",
    "symbol": "Symbol",
    "message_index": "Index",
}


def get_header_name(field_name: str) -> str:
    return FIELD_NAME_TO_HEADER_MAP.get(
        field_name, field_name.replace("_", " ").title()
    )


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.current_fit_data: fit_handler.LocationsFitFileData | None = None
        self.current_selected_waypoint_index: int = -1

        self.file_id_inputs = {}
        self.file_creator_inputs = {}
        self.location_settings_inputs = {}
        self.waypoint_details_inputs = {}
        self.add_location_settings_btn = None  # Initialize button attribute

        self.open_locations_file_action.triggered.connect(self.slot_open_locations_file)
        self.save_new_locations_file_action.triggered.connect(
            self.slot_save_new_locations_file
        )

        self.add_waypoint_btn.clicked.connect(self.slot_add_waypoint)
        self.delete_waypoint_btn.clicked.connect(self.slot_delete_waypoint)
        self.save_waypoint_changes_btn.clicked.connect(self.slot_save_waypoint_changes)

        self.waypoints_table_widget.itemSelectionChanged.connect(
            self.slot_waypoint_selection_changed
        )

        self._setup_waypoints_table()
        self._clear_all_forms_and_tables()
        self.waypoint_details_groupbox.setEnabled(False)

    def _setup_waypoints_table(self):
        self.waypoints_table_widget.setColumnCount(8)
        headers = [
            get_header_name("message_index"),
            get_header_name("name"),
            get_header_name("latitude"),
            get_header_name("longitude"),
            get_header_name("altitude"),
            get_header_name("timestamp"),
            get_header_name("symbol"),
            get_header_name("description"),
        ]
        self.waypoints_table_widget.setHorizontalHeaderLabels(headers)
        self.waypoints_table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.waypoints_table_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.waypoints_table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def _clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    sub_layout = item.layout()
                    if sub_layout is not None:
                        self._clear_layout(sub_layout)

    def _populate_file_id_form(self):
        self._clear_layout(self.file_id_form_layout)
        self.file_id_inputs.clear()
        if not self.current_fit_data or not self.current_fit_data.header:
            return

        header = self.current_fit_data.header

        self.file_id_inputs["file_type"] = QComboBox()
        for ft in FileType:
            self.file_id_inputs["file_type"].addItem(ft.name, ft)
        if header.file_type:
            self.file_id_inputs["file_type"].setCurrentIndex(
                self.file_id_inputs["file_type"].findData(header.file_type)
            )
        self.file_id_form_layout.addRow(
            get_header_name("file_type"), self.file_id_inputs["file_type"]
        )

        self.file_id_inputs["manufacturer"] = QComboBox()
        for mfg in Manufacturer:
            self.file_id_inputs["manufacturer"].addItem(mfg.name, mfg)
        if header.manufacturer:
            self.file_id_inputs["manufacturer"].setCurrentIndex(
                self.file_id_inputs["manufacturer"].findData(header.manufacturer)
            )
        self.file_id_inputs["manufacturer"].setEnabled(False)
        self.file_id_form_layout.addRow(
            get_header_name("manufacturer"), self.file_id_inputs["manufacturer"]
        )

        self.file_id_inputs["product"] = QComboBox()
        if header.manufacturer == Manufacturer.GARMIN:
            for gp in GarminProduct:
                self.file_id_inputs["product"].addItem(gp.name, gp)
            if header.product:
                self.file_id_inputs["product"].setCurrentIndex(
                    self.file_id_inputs["product"].findData(header.product)
                )
        else:
            self.file_id_inputs["product"] = QLineEdit(
                str(header.product) if header.product is not None else ""
            )
        self.file_id_form_layout.addRow(
            get_header_name("product"), self.file_id_inputs["product"]
        )

        self.file_id_inputs["serial_number"] = QLineEdit(
            str(header.serial_number) if header.serial_number is not None else ""
        )
        self.file_id_form_layout.addRow(
            get_header_name("serial_number"), self.file_id_inputs["serial_number"]
        )

        self.file_id_inputs["time_created"] = QDateTimeEdit(
            header.time_created
            if header.time_created
            else QDateTime.currentDateTimeUtc()
        )
        self.file_id_inputs["time_created"].setCalendarPopup(True)
        self.file_id_inputs["time_created"].setDisplayFormat("yyyy-MM-dd HH:mm:ss t")
        self.file_id_form_layout.addRow(
            get_header_name("time_created"), self.file_id_inputs["time_created"]
        )

        self.file_id_inputs["product_name"] = QLineEdit(header.product_name or "")
        self.file_id_form_layout.addRow(
            get_header_name("product_name"), self.file_id_inputs["product_name"]
        )

    def _populate_file_creator_form(self):
        self._clear_layout(self.file_creator_form_layout)
        self.file_creator_inputs.clear()
        if not self.current_fit_data or not self.current_fit_data.creator:
            return

        creator = self.current_fit_data.creator
        self.file_creator_inputs["software_version"] = QLineEdit(
            str(creator.software_version)
            if creator.software_version is not None
            else ""
        )
        self.file_creator_form_layout.addRow(
            get_header_name("software_version"),
            self.file_creator_inputs["software_version"],
        )
        self.file_creator_inputs["hardware_version"] = QLineEdit(
            str(creator.hardware_version)
            if creator.hardware_version is not None
            else ""
        )
        self.file_creator_form_layout.addRow(
            get_header_name("hardware_version"),
            self.file_creator_inputs["hardware_version"],
        )

    def _populate_location_settings_form(self):
        self._clear_layout(self.location_settings_form_layout)
        self.location_settings_inputs.clear()
        # Disconnect previous button if it exists, to avoid multiple connections
        if self.add_location_settings_btn:
            try:
                self.add_location_settings_btn.clicked.disconnect(
                    self.slot_add_default_location_settings
                )
            except RuntimeError:  # Was not connected or already disconnected
                pass
            self.add_location_settings_btn = None

        if not self.current_fit_data or not self.current_fit_data.settings:
            info_label = QLabel("Location Settings message not present in this file.")
            self.location_settings_form_layout.addRow(info_label)

            self.add_location_settings_btn = QPushButton(
                "Add Default Location Settings"
            )
            self.add_location_settings_btn.clicked.connect(
                self.slot_add_default_location_settings
            )
            self.location_settings_form_layout.addRow(self.add_location_settings_btn)
            return

        settings = self.current_fit_data.settings
        self.location_settings_inputs["waypoint_setting"] = QComboBox()
        for ls_enum_member in FitLocationSettingsEnum:
            self.location_settings_inputs["waypoint_setting"].addItem(
                ls_enum_member.name, ls_enum_member
            )

        if settings.waypoint_setting:
            self.location_settings_inputs["waypoint_setting"].setCurrentIndex(
                self.location_settings_inputs["waypoint_setting"].findData(
                    settings.waypoint_setting
                )
            )
        elif list(
            FitLocationSettingsEnum
        ):  # If enum is not empty, select first as default in combobox
            self.location_settings_inputs["waypoint_setting"].setCurrentIndex(0)

        self.location_settings_form_layout.addRow(
            get_header_name("waypoint_setting"),
            self.location_settings_inputs["waypoint_setting"],
        )

    def _populate_waypoints_table(self):
        self.waypoints_table_widget.setRowCount(0)
        if self.current_fit_data and self.current_fit_data.waypoints:
            self.waypoints_table_widget.setRowCount(
                len(self.current_fit_data.waypoints)
            )
            for row_idx, wp_data in enumerate(self.current_fit_data.waypoints):
                self.waypoints_table_widget.setItem(
                    row_idx,
                    0,
                    QTableWidgetItem(
                        str(
                            wp_data.message_index
                            if wp_data.message_index is not None
                            else row_idx
                        )
                    ),
                )
                self.waypoints_table_widget.setItem(
                    row_idx, 1, QTableWidgetItem(wp_data.name or "")
                )
                self.waypoints_table_widget.setItem(
                    row_idx,
                    2,
                    QTableWidgetItem(
                        f"{wp_data.latitude:.6f}"
                        if wp_data.latitude is not None
                        else "N/A"
                    ),
                )
                self.waypoints_table_widget.setItem(
                    row_idx,
                    3,
                    QTableWidgetItem(
                        f"{wp_data.longitude:.6f}"
                        if wp_data.longitude is not None
                        else "N/A"
                    ),
                )
                self.waypoints_table_widget.setItem(
                    row_idx,
                    4,
                    QTableWidgetItem(
                        str(wp_data.altitude) if wp_data.altitude is not None else "N/A"
                    ),
                )
                self.waypoints_table_widget.setItem(
                    row_idx,
                    5,
                    QTableWidgetItem(
                        str(
                            wp_data.timestamp.strftime("%Y-%m-%d %H:%M:%S %Z")
                            if wp_data.timestamp
                            else "N/A"
                        )
                    ),
                )
                self.waypoints_table_widget.setItem(
                    row_idx,
                    6,
                    QTableWidgetItem(
                        str(wp_data.symbol) if wp_data.symbol is not None else "N/A"
                    ),
                )
                self.waypoints_table_widget.setItem(
                    row_idx, 7, QTableWidgetItem(wp_data.description or "")
                )
                self.waypoints_table_widget.item(row_idx, 0).setData(
                    Qt.UserRole, row_idx
                )
        self.waypoints_table_widget.resizeColumnsToContents()

    def _populate_waypoint_details_form(self, waypoint_data):
        self._clear_layout(self.waypoint_details_form_layout)
        self.waypoint_details_inputs.clear()

        if waypoint_data:
            self.waypoint_details_groupbox.setEnabled(True)
            self.waypoint_details_inputs["name"] = QLineEdit(waypoint_data.name or "")
            self.waypoint_details_form_layout.addRow(
                get_header_name("name"), self.waypoint_details_inputs["name"]
            )

            self.waypoint_details_inputs["description"] = QLineEdit(
                waypoint_data.description or ""
            )
            self.waypoint_details_form_layout.addRow(
                get_header_name("description"),
                self.waypoint_details_inputs["description"],
            )

            self.waypoint_details_inputs["latitude"] = QDoubleSpinBox()
            self.waypoint_details_inputs["latitude"].setRange(-90.0, 90.0)
            self.waypoint_details_inputs["latitude"].setDecimals(6)
            if waypoint_data.latitude is not None:
                self.waypoint_details_inputs["latitude"].setValue(
                    waypoint_data.latitude
                )
            self.waypoint_details_form_layout.addRow(
                get_header_name("latitude"), self.waypoint_details_inputs["latitude"]
            )

            self.waypoint_details_inputs["longitude"] = QDoubleSpinBox()
            self.waypoint_details_inputs["longitude"].setRange(-180.0, 180.0)
            self.waypoint_details_inputs["longitude"].setDecimals(6)
            if waypoint_data.longitude is not None:
                self.waypoint_details_inputs["longitude"].setValue(
                    waypoint_data.longitude
                )
            self.waypoint_details_form_layout.addRow(
                get_header_name("longitude"), self.waypoint_details_inputs["longitude"]
            )

            self.waypoint_details_inputs["altitude"] = QDoubleSpinBox()
            self.waypoint_details_inputs["altitude"].setRange(-1000, 10000)
            self.waypoint_details_inputs["altitude"].setDecimals(2)
            if waypoint_data.altitude is not None:
                self.waypoint_details_inputs["altitude"].setValue(
                    waypoint_data.altitude
                )
            self.waypoint_details_form_layout.addRow(
                get_header_name("altitude"), self.waypoint_details_inputs["altitude"]
            )

            self.waypoint_details_inputs["timestamp"] = QDateTimeEdit(
                waypoint_data.timestamp
                if waypoint_data.timestamp
                else QDateTime.currentDateTimeUtc()
            )
            self.waypoint_details_inputs["timestamp"].setCalendarPopup(True)
            self.waypoint_details_inputs["timestamp"].setDisplayFormat(
                "yyyy-MM-dd HH:mm:ss t"
            )
            self.waypoint_details_form_layout.addRow(
                get_header_name("timestamp"), self.waypoint_details_inputs["timestamp"]
            )

            self.waypoint_details_inputs["symbol"] = QLineEdit(
                str(waypoint_data.symbol) if waypoint_data.symbol is not None else ""
            )
            self.waypoint_details_form_layout.addRow(
                get_header_name("symbol"), self.waypoint_details_inputs["symbol"]
            )
        else:
            self.waypoint_details_groupbox.setEnabled(False)

    def _clear_all_forms_and_tables(self):
        self._clear_layout(self.file_id_form_layout)
        self.file_id_inputs.clear()
        self._clear_layout(self.file_creator_form_layout)
        self.file_creator_inputs.clear()

        # Clear location settings form specifically (label/button or combobox)
        self._clear_layout(self.location_settings_form_layout)
        self.location_settings_inputs.clear()
        if self.add_location_settings_btn:
            try:
                self.add_location_settings_btn.clicked.disconnect(
                    self.slot_add_default_location_settings
                )
            except RuntimeError:
                pass
            self.add_location_settings_btn = None  # Ensure it's cleared

        self.waypoints_table_widget.setRowCount(0)
        self._populate_waypoint_details_form(None)

    @Slot()
    def slot_open_locations_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Locations.fit File", "", "FIT Files (*.fit);;All Files (*)"
        )
        if file_path:
            self.statusbar.showMessage(f"Opening {file_path}...")
            self._clear_all_forms_and_tables()
            self.current_fit_data = fit_handler.read_fit_file(file_path)

            self._populate_file_id_form()
            self._populate_file_creator_form()
            self._populate_location_settings_form()
            self._populate_waypoints_table()
            self._populate_waypoint_details_form(None)

            if self.current_fit_data.errors:
                errors_str = "\n".join(self.current_fit_data.errors)
                QMessageBox.warning(
                    self,
                    "Warning Reading FIT File",
                    f"Encountered issues reading {file_path}:\n{errors_str}\n\nSome data may be incomplete or missing.",
                )
                self.statusbar.showMessage(
                    f"Warning reading {file_path}. Some data may be missing."
                )
            else:
                self.statusbar.showMessage(f"Successfully opened {file_path}.")

    @Slot()
    def slot_waypoint_selection_changed(self):
        selected_items = self.waypoints_table_widget.selectedItems()
        if selected_items:
            selected_row = selected_items[0].row()
            original_data_index_item = self.waypoints_table_widget.item(selected_row, 0)
            if original_data_index_item:
                original_data_index = original_data_index_item.data(Qt.UserRole)
                if self.current_fit_data and 0 <= original_data_index < len(
                    self.current_fit_data.waypoints
                ):
                    self.current_selected_waypoint_index = original_data_index
                    selected_wp_data = self.current_fit_data.waypoints[
                        original_data_index
                    ]
                    self._populate_waypoint_details_form(selected_wp_data)
                    return
        self.current_selected_waypoint_index = -1
        self._populate_waypoint_details_form(None)

    def _update_current_fit_data_from_forms(self):
        if not self.current_fit_data:
            self.current_fit_data = fit_handler.LocationsFitFileData()

        if self.file_id_form_layout.count() > 0:
            if not self.current_fit_data.header:
                self.current_fit_data.header = fit_handler.FitHeaderData()
            if "file_type" in self.file_id_inputs:
                self.current_fit_data.header.file_type = self.file_id_inputs[
                    "file_type"
                ].currentData()
            if "manufacturer" in self.file_id_inputs:
                self.current_fit_data.header.manufacturer = self.file_id_inputs[
                    "manufacturer"
                ].currentData()
            if "product" in self.file_id_inputs:
                if isinstance(self.file_id_inputs["product"], QComboBox):
                    self.current_fit_data.header.product = self.file_id_inputs[
                        "product"
                    ].currentData()
                elif isinstance(self.file_id_inputs["product"], QLineEdit):
                    try:
                        self.current_fit_data.header.product = (
                            int(self.file_id_inputs["product"].text())
                            if self.file_id_inputs["product"].text()
                            else None
                        )
                    except ValueError:
                        self.current_fit_data.header.product = None
            if "serial_number" in self.file_id_inputs:
                try:
                    self.current_fit_data.header.serial_number = (
                        int(self.file_id_inputs["serial_number"].text())
                        if self.file_id_inputs["serial_number"].text()
                        else None
                    )
                except ValueError:
                    self.current_fit_data.header.serial_number = None
            if "time_created" in self.file_id_inputs:
                self.current_fit_data.header.time_created = (
                    self.file_id_inputs["time_created"]
                    .dateTime()
                    .toPython()
                    .replace(tzinfo=timezone.utc)
                )
            if "product_name" in self.file_id_inputs:
                self.current_fit_data.header.product_name = (
                    self.file_id_inputs["product_name"].text() or None
                )
        elif not self.current_fit_data.header:
            self.current_fit_data.header = None

        if self.file_creator_form_layout.count() > 0:
            if not self.current_fit_data.creator:
                self.current_fit_data.creator = fit_handler.FitCreatorData()
            if "software_version" in self.file_creator_inputs:
                try:
                    self.current_fit_data.creator.software_version = (
                        int(self.file_creator_inputs["software_version"].text())
                        if self.file_creator_inputs["software_version"].text()
                        else None
                    )
                except ValueError:
                    self.current_fit_data.creator.software_version = None
            if "hardware_version" in self.file_creator_inputs:
                try:
                    self.current_fit_data.creator.hardware_version = (
                        int(self.file_creator_inputs["hardware_version"].text())
                        if self.file_creator_inputs["hardware_version"].text()
                        else None
                    )
                except ValueError:
                    self.current_fit_data.creator.hardware_version = None
        elif not self.current_fit_data.creator:
            self.current_fit_data.creator = None

        if self.location_settings_form_layout.count() > 0:
            if not self.current_fit_data.settings:
                self.current_fit_data.settings = fit_handler.FitLocationSettingData()
            if "waypoint_setting" in self.location_settings_inputs:
                self.current_fit_data.settings.waypoint_setting = (
                    self.location_settings_inputs["waypoint_setting"].currentData()
                )
        elif not self.current_fit_data.settings:
            self.current_fit_data.settings = None

    @Slot()
    def slot_save_new_locations_file(self):
        self._update_current_fit_data_from_forms()

        if not self.current_fit_data or (
            not self.current_fit_data.header and not self.current_fit_data.waypoints
        ):
            QMessageBox.information(self, "No Data", "No FIT data to save.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Locations.fit File",
            "Locations_modified.fit",
            "FIT Files (*.fit);;All Files (*)",
        )
        if file_path:
            self.statusbar.showMessage(f"Saving to {file_path}...")
            errors = fit_handler.write_fit_file(file_path, self.current_fit_data)
            if errors:
                errors_str = "\n".join(errors)
                QMessageBox.critical(
                    self,
                    "Error Saving FIT File",
                    f"Could not save {file_path}:\n{errors_str}",
                )
                self.statusbar.showMessage(f"Error saving {file_path}.")
            else:
                self.statusbar.showMessage(f"Successfully saved to {file_path}.")
                QMessageBox.information(
                    self, "File Saved", f"Successfully saved to {file_path}."
                )

    @Slot()
    def slot_add_waypoint(self):
        if not self.current_fit_data:
            self.current_fit_data = fit_handler.LocationsFitFileData()
            if not self.current_fit_data.header:
                self.current_fit_data.header = fit_handler.FitHeaderData()
            if not self.current_fit_data.creator:
                self.current_fit_data.creator = fit_handler.FitCreatorData()
            if not self.current_fit_data.settings:
                self.current_fit_data.settings = fit_handler.FitLocationSettingData(
                    waypoint_setting=FitLocationSettingsEnum.WAYPOINT_FORMAT
                )

            self._populate_file_id_form()
            self._populate_file_creator_form()
            self._populate_location_settings_form()

        new_wp_index = len(self.current_fit_data.waypoints)
        new_wp = fit_handler.FitLocationData(
            name=f"New Waypoint {new_wp_index}",
            description="Added via GUI",
            latitude=0.0,
            longitude=0.0,
            altitude=0.0,
            timestamp=datetime.now(timezone.utc),
            symbol=0,
            message_index=new_wp_index,
        )
        self.current_fit_data.waypoints.append(new_wp)

        row_count = self.waypoints_table_widget.rowCount()
        self.waypoints_table_widget.insertRow(row_count)
        self.waypoints_table_widget.setItem(
            row_count, 0, QTableWidgetItem(str(new_wp.message_index))
        )
        self.waypoints_table_widget.setItem(row_count, 1, QTableWidgetItem(new_wp.name))
        self.waypoints_table_widget.setItem(
            row_count, 2, QTableWidgetItem(f"{new_wp.latitude:.6f}")
        )
        self.waypoints_table_widget.setItem(
            row_count, 3, QTableWidgetItem(f"{new_wp.longitude:.6f}")
        )
        self.waypoints_table_widget.setItem(
            row_count, 4, QTableWidgetItem(str(new_wp.altitude))
        )
        self.waypoints_table_widget.setItem(
            row_count,
            5,
            QTableWidgetItem(new_wp.timestamp.strftime("%Y-%m-%d %H:%M:%S %Z")),
        )
        self.waypoints_table_widget.setItem(
            row_count, 6, QTableWidgetItem(str(new_wp.symbol))
        )
        self.waypoints_table_widget.setItem(
            row_count, 7, QTableWidgetItem(new_wp.description)
        )
        self.waypoints_table_widget.item(row_count, 0).setData(
            Qt.UserRole, new_wp_index
        )

        self.waypoints_table_widget.selectRow(row_count)
        self.statusbar.showMessage(
            f"Added '{new_wp.name}'. Edit details and click 'Apply Changes'."
        )

    @Slot()
    def slot_delete_waypoint(self):
        selected_items = self.waypoints_table_widget.selectedItems()
        if not selected_items:
            QMessageBox.information(
                self, "No Selection", "Select a waypoint to delete."
            )
            return

        selected_row = selected_items[0].row()
        original_data_index_item = self.waypoints_table_widget.item(selected_row, 0)
        if not original_data_index_item:
            return

        original_data_index = original_data_index_item.data(Qt.UserRole)

        if self.current_fit_data and 0 <= original_data_index < len(
            self.current_fit_data.waypoints
        ):
            del self.current_fit_data.waypoints[original_data_index]
            for i, wp in enumerate(self.current_fit_data.waypoints):
                wp.message_index = i
            self._populate_waypoints_table()
            self._populate_waypoint_details_form(None)
            self.statusbar.showMessage(
                "Waypoint deleted. Save the file to persist changes."
            )
        else:
            QMessageBox.warning(self, "Error", "Could not delete selected waypoint.")

    @Slot()
    def slot_save_waypoint_changes(self):
        if (
            self.current_selected_waypoint_index < 0
            or not self.current_fit_data
            or self.current_selected_waypoint_index
            >= len(self.current_fit_data.waypoints)
        ):
            QMessageBox.warning(
                self,
                "No Waypoint Selected",
                "Select a waypoint from the table to edit its details.",
            )
            return

        wp_data_to_update = self.current_fit_data.waypoints[
            self.current_selected_waypoint_index
        ]

        try:
            wp_data_to_update.name = self.waypoint_details_inputs["name"].text() or None
            wp_data_to_update.description = (
                self.waypoint_details_inputs["description"].text() or None
            )
            wp_data_to_update.latitude = self.waypoint_details_inputs[
                "latitude"
            ].value()
            wp_data_to_update.longitude = self.waypoint_details_inputs[
                "longitude"
            ].value()
            wp_data_to_update.altitude = self.waypoint_details_inputs[
                "altitude"
            ].value()
            dt_py = self.waypoint_details_inputs["timestamp"].dateTime().toPython()
            if dt_py.tzinfo is None:
                wp_data_to_update.timestamp = dt_py.replace(tzinfo=timezone.utc)
            else:
                wp_data_to_update.timestamp = dt_py.astimezone(timezone.utc)

            symbol_text = self.waypoint_details_inputs["symbol"].text()
            wp_data_to_update.symbol = (
                int(symbol_text) if symbol_text.isdigit() else None
            )
        except KeyError as e:
            QMessageBox.critical(self, "Error", f"Missing input field reference: {e}")
            return
        except ValueError as e:
            QMessageBox.critical(self, "Input Error", f"Invalid value for a field: {e}")
            return

        table_row_to_update = -1
        for r in range(self.waypoints_table_widget.rowCount()):
            item_data = self.waypoints_table_widget.item(r, 0).data(Qt.UserRole)
            if item_data == self.current_selected_waypoint_index:
                table_row_to_update = r
                break

        if table_row_to_update != -1:
            self.waypoints_table_widget.item(table_row_to_update, 1).setText(
                wp_data_to_update.name or ""
            )
            self.waypoints_table_widget.item(table_row_to_update, 2).setText(
                f"{wp_data_to_update.latitude:.6f}"
                if wp_data_to_update.latitude is not None
                else "N/A"
            )
            self.waypoints_table_widget.item(table_row_to_update, 3).setText(
                f"{wp_data_to_update.longitude:.6f}"
                if wp_data_to_update.longitude is not None
                else "N/A"
            )
            self.waypoints_table_widget.item(table_row_to_update, 4).setText(
                str(wp_data_to_update.altitude)
                if wp_data_to_update.altitude is not None
                else "N/A"
            )
            self.waypoints_table_widget.item(table_row_to_update, 5).setText(
                wp_data_to_update.timestamp.strftime("%Y-%m-%d %H:%M:%S %Z")
                if wp_data_to_update.timestamp
                else "N/A"
            )
            self.waypoints_table_widget.item(table_row_to_update, 6).setText(
                str(wp_data_to_update.symbol)
                if wp_data_to_update.symbol is not None
                else "N/A"
            )
            self.waypoints_table_widget.item(table_row_to_update, 7).setText(
                wp_data_to_update.description or ""
            )

        self.statusbar.showMessage(
            f"Changes applied to '{wp_data_to_update.name}'. Save the file to persist."
        )

    @Slot()
    def slot_add_default_location_settings(self):
        if not self.current_fit_data:
            self.current_fit_data = fit_handler.LocationsFitFileData()
            # Ensure other parts of current_fit_data are initialized if needed
            if (
                not self.current_fit_data.header
            ):  # Example: ensure header exists for consistency
                self.current_fit_data.header = fit_handler.FitHeaderData()

        default_setting_value = None
        if list(FitLocationSettingsEnum):  # Check if enum is not empty
            default_setting_value = list(FitLocationSettingsEnum)[0]
        else:
            QMessageBox.warning(
                self,
                "Enum Error",
                "LocationSettings Enum is empty. Cannot set a default.",
            )
            return

        self.current_fit_data.settings = fit_handler.FitLocationSettingData(
            waypoint_setting=default_setting_value
        )
        self.statusbar.showMessage(
            "Default Location Settings added. You can now select a value."
        )
        self._populate_location_settings_form()  # Refresh the form to show the QComboBox


def main_app():
    app = QApplication(sys.argv)
    try:
        window = MainWindow()
        window.show()
    except Exception as e:
        print(f"Error initializing MainWindow: {e}")
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setText("Error Initializing UI")
        error_dialog.setInformativeText(
            f"Could not load the main window UI. Ensure 'gui/ui_new_main_window.py' is correctly compiled from 'gui/new_main_window.ui'.\n\nDetails: {e}"
        )
        error_dialog.setWindowTitle("UI Load Error")
        error_dialog.exec_()
        sys.exit(1)

    sys.exit(app.exec())


if __name__ == "__main__":
    main_app()
