
import webbrowser

from car_edit_ui import CarAddUI, CarEditUI

from shared import (NumberFormat, MAIN_FONT, BUTTON_CSS,
                    INFO_TITLE_COLOR_HOVER, INFO_TITLE_COLOR_PRESSED, INFO_TITLE_COLOR,
                    FONT_SIZE_LARGE, FONT_SIZE_MED, FONT_SIZE_SMALL,
                    FONT_SIZE_HEADER_LARGE, FONT_SIZE_HEADER_MED, FONT_SIZE_HEADER_SMALL)

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

INFO_WIDTH = 384

# INFO_ITEM_COLOR = "#666666"
INFO_ITEM_COLOR = "#444444"


# TODO: make a scroll bar for the main widgets
#  maybe put them into another QVBoxLayout and use a scrollbar?
#  unless it won't work like that
class CarInfoUI(QVBoxLayout):
    def __init__(self, parent):
        super().__init__()
        self._parent = parent
        self.setContentsMargins(QMargins(8, 8, 8, 8))
        self.setSpacing(8)
        
        self.info_layout = QVBoxLayout()
        self.info_widget = QWidget()
        self.scroll_area = QScrollArea()
        
        self.listing = ListingUI(self)
        self.engine = EngineUI(self)
        self.car = CarUI(self)
        self.mpg = MilesPerGallonUI(self)
        
        self.car_edit_ui = CarEditUI(self)
        
        self.edit_car = QPushButton("Edit Info")
        self.edit_car.setToolTip("Edit the information above")
        self.edit_car.setFixedHeight(32)
        self.edit_car.setFixedWidth(INFO_WIDTH)
        self.edit_car.setFont(QFont(MAIN_FONT, FONT_SIZE_SMALL))
        self.edit_car.setStyleSheet(BUTTON_CSS)
        self.edit_car.clicked.connect(self.OnEditInfoBtnClick)
        self.edit_car.hide()

        self.info_layout.setContentsMargins(QMargins(0, 0, 0, 0))

        self.info_widget.setLayout(self.info_layout)
        self.scroll_area.setWidget(self.info_widget)
        
        self.scroll_area.setFocusPolicy(Qt.NoFocus)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setFixedWidth(INFO_WIDTH)
        # self.scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.scroll_area.setWidgetResizable(True)
        # self.scroll_area.adjustSize()
        self.scroll_area.setContentsMargins(QMargins(0, 0, 0, 0))
        self.scroll_area.setStyleSheet(
            "border: 0px solid;"
            "border-color: #006600;"
        )
        
        self.info_layout.addWidget(self.listing)
        self.info_layout.addWidget(self.engine)
        self.info_layout.addWidget(self.car)
        self.info_layout.addWidget(self.mpg)
        self.info_layout.addStretch(1)  # dynamic resizing space

        self.addWidget(self.scroll_area)
        self.addWidget(self.edit_car)
        
        self.current_car = None
    
    @pyqtSlot()
    def OnEditInfoBtnClick(self):
        car_obj = self._parent.GetCurrentCar()
        self.car_edit_ui.ShowUI(car_obj)


class BaseCategory(QWidget):
    def __init__(self, parent, title):
        super().__init__()
        self.setContentsMargins(QMargins(0, 0, 0, 0))
        # self.setContentsMargins(QMargins(4, 4, 4, 4))
        # self.current_car = None
        self.parent = parent
        
        # self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.setFocusPolicy(Qt.NoFocus)
        
        self.setStyleSheet(
            # set to 2px for debugging, 0px by default
            "border: 0px solid;"
            "border-color: #006600;"
            # "background-color: #666666;"
            "color: #CCCCCC;"
        )
        
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(QMargins(0, 0, 0, 0))
        
        title_widget_height = 32
        
        self.title_widget = QWidget()
        self.title_widget.setFixedWidth(INFO_WIDTH)
        self.title_widget.setFixedHeight(title_widget_height)
        
        self.title_layout = QGridLayout()
        self.title_layout.setContentsMargins(QMargins(0, 0, 0, 0))
        
        self.button_label = QPushButton(title)
        self.button_label.setFocusPolicy(Qt.NoFocus)
        self.button_label.setFixedHeight(title_widget_height)
        self.button_label.setMaximumWidth(INFO_WIDTH)
        self.button_label.setFont(QFont(MAIN_FONT, FONT_SIZE_LARGE))
        
        # self.button_label.setStyleSheet("background-color: #666666;")
        self.button_label.setStyleSheet(f"""
            QPushButton         {{ background-color: {INFO_TITLE_COLOR}; }}
            QPushButton:hover   {{ background-color: {INFO_TITLE_COLOR_HOVER} }}
            QPushButton:pressed {{ background-color: {INFO_TITLE_COLOR_PRESSED} }}
        """)
        
        self.button_label.clicked.connect(self.OnCategoryTitlePress)
        
        self.info_widget = QWidget()
        self.info_widget.setFixedWidth(INFO_WIDTH)
        self.info_widget.setStyleSheet("background-color: #333333; color: #CCCCCC;")
        
        self.info_layout = QVBoxLayout()
        self.SetInfoLayoutSpacing(8)
        
        self.title_widget.setLayout(self.title_layout)
        self.title_layout.addWidget(self.button_label)
        
        self.info_widget.setLayout(self.info_layout)
        
        self.main_layout.addWidget(self.title_widget)
        self.main_layout.addWidget(self.info_widget)
        
        self.setLayout(self.main_layout)
        
        self.show_info_toggle = True
        self.hide()
    
    @pyqtSlot()  # wtf does this do
    def OnCategoryTitlePress(self):
        self.show_info_toggle = not self.show_info_toggle
        
        if self.show_info_toggle:
            self.info_widget.show()
        else:
            self.info_widget.hide()
        
    def SetInfoLayoutSpacing(self, spacing):
        self.info_layout.setSpacing(spacing)
        self.info_layout.setContentsMargins(QMargins(spacing, spacing, spacing, spacing))
            
    def Reset(self):
        self.hide()


class InfoTable(QTableView):
    def __init__(self, parent):
        super().__init__()
        self._parent = parent
        
        self.setStyleSheet(
            # set to 2px for debugging, 0px by default
            "border: 0px solid;"
            "border-color: #006600;"
            # "background-color: #666666;"
            "color: #CCCCCC;"
        )

        self.info_table = QStandardItemModel()
        self._InitTableView()
        
        self.row = 0
        
    def _InitTableView(self):
        self.setFocusPolicy(Qt.NoFocus)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setVisible(False)
        self.horizontalScrollBar().setStyleSheet("QScrollBar {height:0px;}")
        self.verticalScrollBar().setStyleSheet("QScrollBar {height:0px;}")
    
        # fixes a dumb gap made by this to the right, took a while to figure out
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    
        self.setModel(self.info_table)
        self.setMaximumSize(INFO_WIDTH, 64)
        
        self.setFont(QFont(MAIN_FONT, FONT_SIZE_SMALL))
        self.setStyleSheet(f"""
            QTableView:item
            {{
                padding: 6px;
                border: 0px;
                outline: 0;
            }}

            QTableView
            {{
                background-color: {INFO_ITEM_COLOR};
            }}
        """)

        self.row_height = 28
        
        self.setRowHeight(0, self.row_height)
        
    def AddTableItem(self, name, value):
        if value:
            value = NumberFormat(value)
            self.info_table.setItem(self.row, 0, QStandardItem(name))
            self.info_table.setItem(self.row, 1, QStandardItem(value))
            self.row += 1
            
    def Reset(self):
        self.info_table = QStandardItemModel()
        self.row = 0
        
    def ResetTableView(self):
        self.setModel(self.info_table)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.verticalHeader().setDefaultSectionSize(self.row_height)
        self.setColumnWidth(0, 128)
        
        height = (self.row_height * self.row)  # + 4  # add 4 when using borders for debugging
        self.setFixedHeight(height)


class InfoList(QTableView):
    def __init__(self, parent, title):
        super().__init__()
        self._parent = parent
        self._title = title
        # self._title = QStandardItem(title)
        # self._title.setTextAlignment(Qt.AlignHCenter)
        
        self.setStyleSheet(
            # set to 2px for debugging, 0px by default
            "border: 0px solid;"
            "border-color: #006600;"
            "color: #CCCCCC;"
        )

        self.info_list = QStandardItemModel()
        self._InitList()
        
        self.row = 1
        
    def _InitList(self):
        self.setFocusPolicy(Qt.NoFocus)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setVisible(False)
        self.horizontalScrollBar().setStyleSheet("QScrollBar {height:0px;}")
        self.verticalScrollBar().setStyleSheet("QScrollBar {height:0px;}")
    
        # fixes a dumb gap made by this to the right, took a while to figure out
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    
        self.setModel(self.info_list)
        self.setMaximumSize(INFO_WIDTH, 64)
        
        self.setFont(QFont(MAIN_FONT, FONT_SIZE_SMALL))
        self.setStyleSheet(f"""
            QTableView:item
            {{
                padding: 6px;
                border: 0px;
                outline: 0;
            }}

            QTableView
            {{
                background-color: {INFO_ITEM_COLOR};
            }}
        """)

        self.row_height = 28
        
        self.setRowHeight(0, self.row_height)
        
        # self.setStyleSheet("background-color: #444444;")
        # self.info_list.setItem(0, 0, self._title)
        
    def AddItem(self, item):
        item = NumberFormat(item)
        if item:
            self.info_list.setItem(self.row, 0, QStandardItem(item))
            self.row += 1
            
    def Reset(self):
        self.info_list = QStandardItemModel()
        # self.info_list.setItem(0, 0, self._title)
        # title = QStandardItem(self._title)
        # title.setTextAlignment(Qt.AlignCenter)
        # self.info_list.setItem(0, 0, title)
        self.row = 0
        
    def ResetList(self):
        self.setModel(self.info_list)
        self.horizontalHeader().setStretchLastSection(True)
        self.setColumnWidth(0, 128)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.verticalHeader().setDefaultSectionSize(self.row_height)
    
        height = (self.row_height * self.row)  # + 4  # add 4 when using borders for debugging
        self.setFixedHeight(height)


# TODO: add that Kelly Blue Book thing to this
#  maybe "listing" { "kelly_blue_book" {} }
class ListingUI(BaseCategory):
    def __init__(self, parent):
        super().__init__(parent, "Listing")
        
        self.sold = QLabel("Sold")
        self.sold.setAlignment(Qt.AlignCenter)
        self.sold.setFixedHeight(32)
        self.sold.setFont(QFont(MAIN_FONT, FONT_SIZE_MED))
        self.sold.setStyleSheet("font-weight: bold; background-color: #990000;")
        self.sold.hide()
        
        self.webpage = QPushButton("Open Webpage")
        self.webpage.setToolTip("Open the URL in your default internet browser")
        self.webpage.setFixedHeight(32)
        self.webpage.setFont(QFont(MAIN_FONT, FONT_SIZE_SMALL))
        self.webpage.setStyleSheet(BUTTON_CSS)
        self.webpage.clicked.connect(self.OnURLBtnClick)
        
        self.description = QLabel("Description")
        self.description.setWordWrap(True)
        # self.description.setAlignment(Qt.AlignLeft)
        self.description.setFont(QFont(MAIN_FONT, FONT_SIZE_SMALL))
        self.description.setStyleSheet("QLabel {background-color: #444444;}")
        self.description.setContentsMargins(QMargins(8, 8, 8, 8))
        
        self.table_view = InfoTable(self)
        
        self.info_layout.addWidget(self.sold)
        self.info_layout.addWidget(self.webpage)
        self.info_layout.addWidget(self.table_view)
        self.info_layout.addWidget(self.description)
        
    def SetInfo(self, listing):
        self.Reset()
        self.table_view.Reset()
        
        if not listing.HasValues():
            return
        self.show()
        
        if listing.sold:
            self.sold.show()
        else:
            self.sold.hide()
        
        if listing.url:
            self.webpage.show()
        else:
            self.webpage.hide()
            
        if listing.price:
            price_str = "$" + NumberFormat(listing.price)
            self.table_view.AddTableItem("Price", price_str)
        
        self.table_view.AddTableItem("Location", listing.location)
        self.table_view.AddTableItem("Date Posted", listing.date_posted)
        
        if listing.description:
            self.description.setText(listing.description)
            self.description.setWordWrap(True)
            # self.description.setAlignment(Qt.AlignLeft)
            self.description.setFont(QFont(MAIN_FONT, FONT_SIZE_SMALL))
            self.description.setStyleSheet("QLabel {background-color: #444444;}")
            self.description.setContentsMargins(QMargins(8, 8, 8, 8))
            
            # self.description.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
            
            self.description.show()
        else:
            self.description.hide()
            
        self.table_view.ResetTableView()
    
    @pyqtSlot()
    def OnURLBtnClick(self):
        car_obj = self.parent.current_car
        car_listing = car_obj.GetItem("listing")
        car_url = car_listing.GetItemValue("url")
        webbrowser.open_new(car_url)


class EngineUI(BaseCategory):
    def __init__(self, parent):
        super().__init__(parent, "Engine")
        self.table_view = InfoTable(self)
        self.info_layout.addWidget(self.table_view)
    
    def SetInfo(self, engine):
        self.Reset()
        self.table_view.Reset()
        
        if not engine.HasValues():
            return
        self.show()

        self.table_view.AddTableItem("Transmission", engine.transmission)
        self.table_view.AddTableItem("Gears", engine.gears)
        self.table_view.AddTableItem("Miles", engine.miles)
        self.table_view.AddTableItem("Horsepower", engine.horsepower)
        self.table_view.AddTableItem("Torque", engine.torque)
        self.table_view.AddTableItem("Cylinders", engine.cylinders)
        self.table_view.AddTableItem("Liter", engine.liter)
        self.table_view.AddTableItem("Valves", engine.valves)

        self.table_view.ResetTableView()


class CarUI(BaseCategory):
    def __init__(self, parent):
        super().__init__(parent, "Car")
        self.table_view = InfoTable(self)
        self.feature_list = InfoList(self, "Features")
        
        self.features_label = QLabel("Features")
        self.features_label.setAlignment(Qt.AlignCenter)
        self.features_label.setFixedHeight(28)
        self.features_label.setFont(QFont(MAIN_FONT, FONT_SIZE_SMALL))
        self.features_label.setStyleSheet("background-color: #444444;")
        self.features_label.hide()
        
        self.info_layout.addWidget(self.table_view)
        self.info_layout.addWidget(self.features_label)
        self.info_layout.addWidget(self.feature_list)
    
    def SetInfo(self, car_info):
        self.Reset()
        self.table_view.Reset()
        self.feature_list.Reset()
        
        if not car_info.HasValues():
            return
        self.show()

        self.table_view.AddTableItem("Exterior Color", car_info.exterior)
        self.table_view.AddTableItem("Interior Color", car_info.interior)
        self.table_view.AddTableItem("Condition", car_info.condition)
        self.table_view.AddTableItem("Radio", car_info.radio)
        self.table_view.AddTableItem("Seating", car_info.seating)
        self.table_view.AddTableItem("Air Bags", car_info.air_bags)
            
        self.table_view.ResetTableView()
        
        if car_info.features:
            self.features_label.show()
            self.feature_list.show()
            for item in car_info.features:
                self.feature_list.AddItem(item.key)
        else:
            self.features_label.hide()
            self.feature_list.hide()
        
        self.feature_list.ResetList()


class MilesPerGallonUI(BaseCategory):
    def __init__(self, parent):
        super().__init__(parent, "Gas Mileage")
        self.table_view = InfoTable(self)
        self.info_layout.addWidget(self.table_view)
    
    def SetInfo(self, mpg):
        self.Reset()
        self.table_view.Reset()
        
        if not mpg.HasValues():
            return
        self.show()

        self.table_view.AddTableItem("City", mpg.city)
        self.table_view.AddTableItem("Highway", mpg.highway)
        self.table_view.AddTableItem("Combined", mpg.combined)
        
        self.table_view.ResetTableView()



