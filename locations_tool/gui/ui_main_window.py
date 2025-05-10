# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'new_main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (
    QCoreApplication,
    QDate,
    QDateTime,
    QLocale,
    QMetaObject,
    QObject,
    QPoint,
    QRect,
    QSize,
    Qt,
    QTime,
    QUrl,
)
from PySide6.QtGui import (
    QAction,
    QBrush,
    QColor,
    QConicalGradient,
    QCursor,
    QFont,
    QFontDatabase,
    QGradient,
    QIcon,
    QImage,
    QKeySequence,
    QLinearGradient,
    QPainter,
    QPalette,
    QPixmap,
    QRadialGradient,
    QTransform,
)
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLayout,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 700)
        self.open_locations_file_action = QAction(MainWindow)
        self.open_locations_file_action.setObjectName("open_locations_file_action")
        self.save_new_locations_file_action = QAction(MainWindow)
        self.save_new_locations_file_action.setObjectName(
            "save_new_locations_file_action"
        )
        self.actionImportGPX = QAction(MainWindow)
        self.actionImportGPX.setObjectName("actionImportGPX")
        self.actionExportGPX = QAction(MainWindow)
        self.actionExportGPX.setObjectName("actionExportGPX")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.main_layout = QVBoxLayout(self.centralwidget)
        self.main_layout.setObjectName("main_layout")
        self.tab_widget = QTabWidget(self.centralwidget)
        self.tab_widget.setObjectName("tab_widget")
        self.file_info_tab = QWidget()
        self.file_info_tab.setObjectName("file_info_tab")
        self.file_info_layout = QVBoxLayout(self.file_info_tab)
        self.file_info_layout.setObjectName("file_info_layout")
        self.file_id_groupbox = QGroupBox(self.file_info_tab)
        self.file_id_groupbox.setObjectName("file_id_groupbox")
        self.file_id_form_layout = QFormLayout(self.file_id_groupbox)
        self.file_id_form_layout.setObjectName("file_id_form_layout")

        self.file_info_layout.addWidget(self.file_id_groupbox)

        self.file_creator_groupbox = QGroupBox(self.file_info_tab)
        self.file_creator_groupbox.setObjectName("file_creator_groupbox")
        self.file_creator_form_layout = QFormLayout(self.file_creator_groupbox)
        self.file_creator_form_layout.setObjectName("file_creator_form_layout")

        self.file_info_layout.addWidget(self.file_creator_groupbox)

        self.location_settings_groupbox = QGroupBox(self.file_info_tab)
        self.location_settings_groupbox.setObjectName("location_settings_groupbox")
        self.location_settings_form_layout = QFormLayout(
            self.location_settings_groupbox
        )
        self.location_settings_form_layout.setObjectName(
            "location_settings_form_layout"
        )

        self.file_info_layout.addWidget(self.location_settings_groupbox)

        self.file_info_spacer = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.file_info_layout.addItem(self.file_info_spacer)

        self.tab_widget.addTab(self.file_info_tab, "")
        self.waypoints_tab = QWidget()
        self.waypoints_tab.setObjectName("waypoints_tab")
        self.waypoints_main_layout = QHBoxLayout(self.waypoints_tab)
        self.waypoints_main_layout.setObjectName("waypoints_main_layout")
        self.waypoints_table_widget = QTableWidget(self.waypoints_tab)
        if self.waypoints_table_widget.columnCount() < 4:
            self.waypoints_table_widget.setColumnCount(4)
        __qtablewidgetitem = QTableWidgetItem()
        self.waypoints_table_widget.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.waypoints_table_widget.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.waypoints_table_widget.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.waypoints_table_widget.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        self.waypoints_table_widget.setObjectName("waypoints_table_widget")
        sizePolicy = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.waypoints_table_widget.sizePolicy().hasHeightForWidth()
        )
        self.waypoints_table_widget.setSizePolicy(sizePolicy)
        self.waypoints_table_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.waypoints_table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.waypoints_main_layout.addWidget(self.waypoints_table_widget)

        self.waypoints_edit_layout = QVBoxLayout()
        self.waypoints_edit_layout.setObjectName("waypoints_edit_layout")
        self.waypoints_edit_layout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.waypoint_details_groupbox = QGroupBox(self.waypoints_tab)
        self.waypoint_details_groupbox.setObjectName("waypoint_details_groupbox")
        self.waypoint_details_form_layout = QFormLayout(self.waypoint_details_groupbox)
        self.waypoint_details_form_layout.setObjectName("waypoint_details_form_layout")

        self.waypoints_edit_layout.addWidget(self.waypoint_details_groupbox)

        self.waypoint_buttons_layout = QHBoxLayout()
        self.waypoint_buttons_layout.setObjectName("waypoint_buttons_layout")
        self.add_waypoint_btn = QPushButton(self.waypoints_tab)
        self.add_waypoint_btn.setObjectName("add_waypoint_btn")

        self.waypoint_buttons_layout.addWidget(self.add_waypoint_btn)

        self.delete_waypoint_btn = QPushButton(self.waypoints_tab)
        self.delete_waypoint_btn.setObjectName("delete_waypoint_btn")

        self.waypoint_buttons_layout.addWidget(self.delete_waypoint_btn)

        self.waypoints_edit_layout.addLayout(self.waypoint_buttons_layout)

        self.save_waypoint_changes_btn = QPushButton(self.waypoints_tab)
        self.save_waypoint_changes_btn.setObjectName("save_waypoint_changes_btn")

        self.waypoints_edit_layout.addWidget(self.save_waypoint_changes_btn)

        self.waypoints_edit_spacer = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.waypoints_edit_layout.addItem(self.waypoints_edit_spacer)

        self.waypoints_main_layout.addLayout(self.waypoints_edit_layout)

        self.tab_widget.addTab(self.waypoints_tab, "")

        self.main_layout.addWidget(self.tab_widget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QToolBar(MainWindow)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolBar)

        self.toolBar.addAction(self.open_locations_file_action)
        self.toolBar.addAction(self.save_new_locations_file_action)
        self.toolBar.addAction(self.actionImportGPX)
        self.toolBar.addAction(self.actionExportGPX)

        self.retranslateUi(MainWindow)

        self.tab_widget.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(MainWindow)

    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(
            QCoreApplication.translate("MainWindow", "FIT Locations Editor", None)
        )
        self.open_locations_file_action.setText(
            QCoreApplication.translate("MainWindow", "Open FIT", None)
        )
        # if QT_CONFIG(tooltip)
        self.open_locations_file_action.setToolTip(
            QCoreApplication.translate("MainWindow", "Open Locations.fit File", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.save_new_locations_file_action.setText(
            QCoreApplication.translate("MainWindow", "Save FIT", None)
        )
        # if QT_CONFIG(tooltip)
        self.save_new_locations_file_action.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Save as new Locations.fit File", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.actionImportGPX.setText(
            QCoreApplication.translate("MainWindow", "Import GPX", None)
        )
        self.actionExportGPX.setText(
            QCoreApplication.translate("MainWindow", "Export GPX", None)
        )
        self.file_id_groupbox.setTitle(
            QCoreApplication.translate("MainWindow", "File ID", None)
        )
        self.file_creator_groupbox.setTitle(
            QCoreApplication.translate("MainWindow", "File Creator", None)
        )
        self.location_settings_groupbox.setTitle(
            QCoreApplication.translate("MainWindow", "Location Settings", None)
        )
        self.tab_widget.setTabText(
            self.tab_widget.indexOf(self.file_info_tab),
            QCoreApplication.translate("MainWindow", "File Info", None),
        )
        ___qtablewidgetitem = self.waypoints_table_widget.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(
            QCoreApplication.translate("MainWindow", "Index", None)
        )
        ___qtablewidgetitem1 = self.waypoints_table_widget.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(
            QCoreApplication.translate("MainWindow", "Name", None)
        )
        ___qtablewidgetitem2 = self.waypoints_table_widget.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(
            QCoreApplication.translate("MainWindow", "Latitude", None)
        )
        ___qtablewidgetitem3 = self.waypoints_table_widget.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(
            QCoreApplication.translate("MainWindow", "Longitude", None)
        )
        self.waypoint_details_groupbox.setTitle(
            QCoreApplication.translate("MainWindow", "Waypoint Details", None)
        )
        self.add_waypoint_btn.setText(
            QCoreApplication.translate("MainWindow", "Add New", None)
        )
        self.delete_waypoint_btn.setText(
            QCoreApplication.translate("MainWindow", "Delete Selected", None)
        )
        self.save_waypoint_changes_btn.setText(
            QCoreApplication.translate("MainWindow", "Apply Changes to Waypoint", None)
        )
        self.tab_widget.setTabText(
            self.tab_widget.indexOf(self.waypoints_tab),
            QCoreApplication.translate("MainWindow", "Waypoints", None),
        )
        self.toolBar.setWindowTitle(
            QCoreApplication.translate("MainWindow", "toolBar", None)
        )

    # retranslateUi
