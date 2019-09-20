from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from shared import (GetDisplayName, DeleteEntireLayout, CenterWindow,
                    BUTTON_CSS, BUTTON_COLOR, BUTTON_COLOR_PRESSED, BUTTON_COLOR_HOVER, MAIN_FONT,
                    INFO_TITLE_COLOR_HOVER, INFO_TITLE_COLOR_PRESSED, INFO_TITLE_COLOR,
                    FONT_SIZE_LARGE, FONT_SIZE_MED, FONT_SIZE_SMALL)

import demez_key_values.demez_key_values as dkv
import url_parser


EDIT_WIDTH = 448

INFO_ITEM_COLOR = "#444444"

TEXT_INPUT_COLOR = "#222222"

BASE_INPUT_PADDING = 2

TEXT_INPUT_PADDING = str(BASE_INPUT_PADDING) + "px"
DISPLAY_KEY_PADDING = str(int(BASE_INPUT_PADDING*2)) + "px"

LOCKED_IMG = "locked.png"
UNLOCKED_IMG = "unlocked.png"

'''
BOOL_BUTTON_CSS = f"""
QPushButton         {{ padding: {TEXT_INPUT_PADDING}; text-align: left; background-color: {TEXT_INPUT_COLOR}; }}
QPushButton:hover   {{ background-color: #262626 }}
QPushButton:pressed {{ background-color: #1a1a1a }}
"""
'''

BOOL_BUTTON_CSS = f"""
QPushButton         {{ padding: {DISPLAY_KEY_PADDING}; text-align: left; background-color: {BUTTON_COLOR}; }}
QPushButton:hover   {{ background-color: {BUTTON_COLOR_HOVER}; }}
QPushButton:pressed {{ background-color: {BUTTON_COLOR_PRESSED}; }}
"""


# maybe move this to where the add car button is?
class CarAddUI(QWidget):
    def __init__(self, parent):
        super().__init__()
        self._parent = parent
        self.main_layout = QHBoxLayout()
        
        self.url_box = QLineEdit()
        self.set_url_btn = QPushButton("Add Car")
        
        self.InitUI()
        
    def InitUI(self):
        self.setWindowTitle("Add Car")
        # relative to top left corner
        # x, y, width, height
        self.setLayout(self.main_layout)
        # self.showMaximized()
        
        self.setStyleSheet(
            # set to 2px for debugging, 0px by default
            "border: 0px solid;"
            "border-color: #0099ff;"
            "background-color: #222222;"
            "color: #CCCCCC;"
            "outline: 0;"
        )
        
        self.setFocusPolicy(Qt.StrongFocus)
        
        self.setFont(QFont(MAIN_FONT, 12))
        
        self.main_layout.setSpacing(8)
        # self.main_layout.setContentsMargins(QMargins(0, 0, 0, 0))
        self.main_layout.setContentsMargins(QMargins(8, 8, 8, 8))
        
        url_layout_height = 32
        
        self.setGeometry(200, 300, 720, url_layout_height + 8)
        
        # center window
        qt_rectangle = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        qt_rectangle.moveCenter(center_point)
        self.move(qt_rectangle.topLeft())

        url_label = QLabel("URL:")
        url_label.setFixedWidth(int(url_layout_height * 1.5))
        url_label.setFixedHeight(url_layout_height)
        url_label.setFont(QFont(MAIN_FONT, FONT_SIZE_SMALL))
        url_label.setAlignment(Qt.AlignCenter)
        url_label.setStyleSheet("QLabel {background-color: " + BUTTON_COLOR + ";}")
        
        self.set_url_btn.setStyleSheet(BUTTON_CSS)
        self.set_url_btn.setFixedWidth(int(url_layout_height * 2.5))
        self.set_url_btn.setFixedHeight(url_layout_height)
        self.set_url_btn.clicked.connect(self.OnAddUrlBtnClick)
        self.set_url_btn.setContentsMargins(QMargins(8, 8, 8, 8))
        self.set_url_btn.setFont(QFont(MAIN_FONT, FONT_SIZE_SMALL))
        
        self.url_box.setFixedHeight(url_layout_height)
        self.url_box.setFont(QFont(MAIN_FONT, FONT_SIZE_SMALL))
        self.url_box.setStyleSheet("background-color: " + BUTTON_COLOR + ";")
        
        # temp
        # self.url_box.setText("https://www.facebook.com/marketplace/item/740191829752000/")
        # self.url_box.setText("https://www.facebook.com/marketplace/item/1318601221623117/")
        # self.url_box.setText("https://www.facebook.com/marketplace/item/1377859972370204/")
        
        self.main_layout.addWidget(url_label)
        self.main_layout.addWidget(self.url_box)
        self.main_layout.addWidget(self.set_url_btn)

    @pyqtSlot()
    def OnAddUrlBtnClick(self):
        url = self.url_box.text()
        dkv_root = url_parser.MakeCarDKVFromURL(url)
        
        try:
            self._parent.AddCar(dkv_root[0])
            self._parent.AddToConfig(dkv_root)

            # select the car we just added
            self._parent.car_list_ui.setCurrentRow(int(dkv_root[0].GetItemValue("id")))
            self._parent.OnCarClick()
        except Exception as F:
            print(str(F))


class CarEditUI(QWidget):
    def __init__(self, parent):
        super().__init__()
        self._parent = parent
        self._car_config = None
        self.setWindowTitle("Edit Car")
        self.setGeometry(0, 0, 720, 950)
        self.setStyleSheet("border: 0px solid; border-color: #0099ff; "
                           "background-color: #222222; color: #CCCCCC; outline: 0;")
        self.setFont(QFont(MAIN_FONT, FONT_SIZE_MED))
        self.hide()
        
        # center window
        CenterWindow(self)
        
        self.main_layout = QVBoxLayout()
        self.item_contents_layout = QVBoxLayout()
        self.item_contents_widget = QWidget()
        self.scroll_area_layout = QVBoxLayout()
        self.scroll_area = QScrollArea()
        
        self.base_settings = BaseSettings(self)
        self.listing = Listing(self)
        self.engine = Engine(self)
        self.car_info = CarInfo(self)
        self.mpg = MilesPerGallon(self)

        self.update_button = QPushButton("Update From URL")
        # self.update_button.setToolTip("Edit the information above")
        self.update_button.setFixedHeight(32)
        self.update_button.setFont(QFont(MAIN_FONT, FONT_SIZE_SMALL))
        self.update_button.setStyleSheet(BUTTON_CSS)
        self.update_button.clicked.connect(self.OnUpdateBtnPress)

        self.save_button = QPushButton("Save")
        # self.save_button.setToolTip("Edit the information above")
        self.save_button.setFixedHeight(32)
        self.save_button.setFont(QFont(MAIN_FONT, FONT_SIZE_SMALL))
        self.save_button.setStyleSheet(BUTTON_CSS)
        self.save_button.clicked.connect(self.OnSaveBtnPress)

        self.setLayout(self.main_layout)
        self.main_layout.addWidget(self.scroll_area)
        self.scroll_area.setLayout(self.scroll_area_layout)

        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: 0px solid; border-color: #0000ff;")

        self.item_contents_layout.addWidget(self.base_settings)
        self.item_contents_layout.addWidget(self.listing)
        self.item_contents_layout.addWidget(self.engine)
        self.item_contents_layout.addWidget(self.car_info)
        self.item_contents_layout.addWidget(self.mpg)
        self.item_contents_layout.addStretch(1)  # dynamic resizing space

        self.scroll_area_layout.addLayout(self.item_contents_layout)
        self.item_contents_widget.setLayout(self.scroll_area_layout)
        self.scroll_area.setWidget(self.item_contents_widget)
        
        self.scroll_area_layout.setSpacing(8)
        self.scroll_area_layout.setContentsMargins(QMargins(0, 0, 0, 0))
        
        self.main_layout.addWidget(self.update_button)
        self.main_layout.addWidget(self.save_button)
        
        self.main_layout.setSpacing(8)
        self.main_layout.setContentsMargins(QMargins(8, 8, 8, 8))
        
    def ShowUI(self, car_config):
        self._car_config = car_config

        self.base_settings.SetInfo(car_config)
        self.listing.SetInfo(car_config)
        self.engine.SetInfo(car_config)
        self.car_info.SetInfo(car_config)
        self.mpg.SetInfo(car_config)
        
        if self.isHidden():
            self.show()
            CenterWindow(self)

        # self.raise_()
        self.activateWindow()

    @pyqtSlot()
    def OnUpdateBtnPress(self):
        # Update all the values
        url = self._car_config.GetItem("listing").GetItemValue("url")
        dkv_root = url_parser.MakeCarDKVFromURL(url)
        try:
            car = dkv_root.GetItem("car")
            self._car_config.GetItem("id").condition = "$LOCKED"
            UpdateUnlockedItems(self._car_config, car)
        except Exception as F:
            print(str(F))

        UpdateCategoryFromCfg(self.base_settings.info_edit)
        UpdateCategoryFromCfg(self.listing.info_edit)
        UpdateCategoryFromCfg(self.engine.info_edit)
        UpdateCategoryFromCfg(self.car_info.info_edit)
        UpdateCategoryFromCfg(self.mpg.info_edit)
        
        # now reload this car
        try:
            self._parent._parent.WriteConfig()
        except Exception as F:
            print(str(F))

    @pyqtSlot()
    def OnSaveBtnPress(self):
        # Update all the values
        UpdateCfg(self.base_settings.info_edit)
        UpdateCfg(self.listing.info_edit)
        UpdateCfg(self.engine.info_edit)
        UpdateCfg(self.car_info.info_edit)
        UpdateCfg(self.mpg.info_edit)
        
        # now reload this car
        try:
            self._parent._parent.WriteConfig()
        except Exception as F:
            print(str(F))


def UpdateCfg(category):
    try:
        for value_field, dkv_item in category.items.items():
            if type(value_field) in {QLineEdit, QPushButton}:
                dkv_item.value = value_field.text()
            elif type(value_field) in {QTextEdit, QPlainTextEdit}:
                dkv_item.value = value_field.toPlainText()
            else:
                print("Unknown Type")
    except Exception as F:
        print(str(F))


def UpdateCategoryFromCfg(category):
    try:
        for value_field, dkv_item in category.items.items():
            if type(value_field) in {QLineEdit, QPushButton, QTextEdit, QPlainTextEdit}:
                value_field.setText(dkv_item.value)
            else:
                print("Unknown Type")
    except Exception as F:
        print(str(F))
        
        
def UpdateUnlockedItems(old_dkv, new_dkv):
    if new_dkv:
        for item in old_dkv.value:
            if item.condition != "$LOCKED":
                new_item = new_dkv.GetItem(item.key)
                if new_item:
                    if type(item.value) == list:
                        UpdateUnlockedItems(item, new_dkv.GetItem(item.key))
                    else:
                        item.value = new_item.value
            else:
                print("temp skipping locked")


class BaseCategory(QWidget):
    def __init__(self, parent, title, key):
        super().__init__()
        self.setContentsMargins(QMargins(0, 0, 0, 0))
        # self.setContentsMargins(QMargins(4, 4, 4, 4))
        # self.current_car = None
        self.parent = parent
        self.car_config = None
        self.info = None
        self.key = key
        
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        
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
        # self.title_widget.setFixedWidth(EDIT_WIDTH)
        self.title_widget.setFixedHeight(title_widget_height)
        
        self.title_layout = QGridLayout()
        self.title_layout.setContentsMargins(QMargins(0, 0, 0, 0))
        
        self.button_label = QPushButton(title)
        self.button_label.setFixedHeight(title_widget_height)
        # self.button_label.setMaximumWidth(EDIT_WIDTH)
        self.button_label.setFont(QFont(MAIN_FONT, FONT_SIZE_LARGE))
        self.button_label.setStyleSheet(f"""
            QPushButton         {{ background-color: {INFO_TITLE_COLOR}; }}
            QPushButton:hover   {{ background-color: {INFO_TITLE_COLOR_HOVER} }}
            QPushButton:pressed {{ background-color: {INFO_TITLE_COLOR_PRESSED} }}
        """)
        
        self.button_label.clicked.connect(self.OnCategoryTitlePress)
        
        self.info_widget = QWidget()
        # self.info_widget.setFixedWidth(EDIT_WIDTH)
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
        # self.show()
    
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
    
    def Reset(self, car_config: dkv.DemezKeyValue):
        # self.show()
        self.car_config = car_config
        self.info = self.car_config.GetItem(self.key)
        
        
class LockButton(QStandardItem):
    def __init__(self, parent):
        super().__init__("X")
        self._parent = parent
        self.setFont(QFont(MAIN_FONT, FONT_SIZE_LARGE))
        # self.setStyleSheet(f"""
        #             QPushButton         {{ background-color: {INFO_TITLE_COLOR}; }}
        #             QPushButton:hover   {{ background-color: {INFO_TITLE_COLOR_HOVER} }}
        #             QPushButton:pressed {{ background-color: {INFO_TITLE_COLOR_PRESSED} }}
        #         """)
        
        self.locked = False

    @pyqtSlot()
    def OnPress(self):
        self.locked = not self.locked
        print("button pressed")
        

class InfoEdit(QVBoxLayout):
    def __init__(self, parent):
        super().__init__()
        self._parent = parent
        self.item_index = 0
        self.row_height = 24
        self.items = {}
        
    def AddButton(self, key, values: tuple):
        row_layout, locked_check, item = self._CreateBaseRow(key, self._parent.info)
        
        button = QPushButton()
        button.setFont(QFont(MAIN_FONT, FONT_SIZE_SMALL))
        button.setFixedHeight(self.row_height)
        button.setLayoutDirection(Qt.LeftToRight)
        button.setStyleSheet(BOOL_BUTTON_CSS)
        button.clicked.connect(lambda: self.ButtonPress(button, values))
        
        if item.value == values[0]:
            button.setText(values[0])
        else:
            button.setText(values[1])

        self.items[button] = item
        row_layout.addWidget(button)
    
    def AddTextEdit(self, key):
        row_layout, locked_check, item = self._CreateBaseRow(key, self._parent.info)
        
        text_edit = QPlainTextEdit(item.value)
        # text_edit.setFixedHeight(self.row_height)
        text_edit.setFont(QFont(MAIN_FONT, FONT_SIZE_SMALL))
        # text_edit.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        text_edit.setStyleSheet(
            f"QPlainTextEdit {{padding: {TEXT_INPUT_PADDING}; background-color: {TEXT_INPUT_COLOR};}}")

        self.items[text_edit] = item
        row_layout.addWidget(text_edit)

    def AddLineEdit(self, key, info=None):
        if not info:
            info = self._parent.info
            
        row_layout, locked_check, item = self._CreateBaseRow(key, info)
        
        line_edit = QLineEdit(item.value)
        line_edit.setFixedHeight(self.row_height)
        line_edit.setFont(QFont(MAIN_FONT, FONT_SIZE_SMALL))
        line_edit.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        line_edit.setStyleSheet(
            f"QLineEdit {{padding: {TEXT_INPUT_PADDING}; background-color: {TEXT_INPUT_COLOR};}}")

        self.items[line_edit] = item
        row_layout.addWidget(line_edit)
        
    # TODO: only allow int or float text fields
    def AddLineEditInt(self, key):
        self.AddLineEdit(key)
        
    def AddLineEditFloat(self, key):
        self.AddLineEdit(key)
        
    def CreateList(self, key):
        pass
        
    def _CreateBaseRow(self, key, info):
        row_layout = QHBoxLayout()
        
        if info:
            item = info.GetItem(key)
            if not item:
                item = info.AddItem(key, "")
        else:
            item = dkv.DemezKeyValue(self._parent.car_config, key, "")
        
        '''
        locked_check = QCheckBox()
        locked_check.stateChanged.connect(lambda: self.ToggleLocked(item))
        if item.condition == "$LOCKED":
            locked_check.setChecked(True)
        '''
        
        lock_layout = QVBoxLayout()
        
        locked_check = QPushButton()
        # locked_check.setToolTip("Locking this will prevent this being changed when updating from the URL")
        locked_check.setToolTip("Any information from the URL will not change this if locked")
        locked_check.setFixedSize(self.row_height, self.row_height)
        # locked_check.setFixedWidth(self.row_height)
        # locked_check.setMinimumHeight(self.row_height)
        locked_check.setLayoutDirection(Qt.LeftToRight)
        locked_check.clicked.connect(lambda: self.ToggleLocked(locked_check, item))
        if item.condition == "$LOCKED":
            locked_check.setIcon(QIcon(LOCKED_IMG))
            
        key_label = QLabel(GetDisplayName(key))
        # key_label.setFixedSize(96, self.row_height)
        key_label.setFixedWidth(96)
        key_label.setMinimumHeight(self.row_height)
        key_label.setFont(QFont(MAIN_FONT, FONT_SIZE_SMALL))
        # key_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        key_label.setAlignment(Qt.AlignLeft)
        key_label.setStyleSheet(f"QLabel {{ padding: {DISPLAY_KEY_PADDING}; }}")
        # key_label.setStyleSheet("QLabel {background-color: " + BUTTON_COLOR + ";}")
        
        lock_layout.addWidget(locked_check)
        lock_layout.addStretch(1)
        
        row_layout.addLayout(lock_layout)
        row_layout.addWidget(key_label)
        
        self.item_index += 1
        self.addLayout(row_layout)
        
        return row_layout, locked_check, item
    
    def Reset(self):
        # ew, this deletes all existing widgets and layouts
        DeleteEntireLayout(self)
            
        self.update()
        self.items = {}
        self.item_index = 0
    
    @pyqtSlot()
    # TODO: can i get image path used for the QIcon for comparing?
    #  if so, use that here instead
    #  maybe make a dictionary of keys that should be locked on saving?
    def ToggleLocked(self, lock_button, dkv_item):
        if dkv_item.condition == "$LOCKED":
            dkv_item.condition = ""
            lock_button.setIcon(QIcon())
        else:
            dkv_item.condition = "$LOCKED"
            lock_button.setIcon(QIcon(LOCKED_IMG))
            
    @pyqtSlot()
    def ButtonPress(self, button, values: tuple):
        if button.text() == values[0]:
            # dkv_item.value = values[1]
            button.setText(values[1])
        else:
            # dkv_item.value = values[0]
            button.setText(values[0])


class BaseSettings(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.setContentsMargins(QMargins(0, 0, 0, 0))
        # self.setContentsMargins(QMargins(4, 4, 4, 4))
        # self.current_car = None
        self.parent = parent
        self.car_config = None
        self.info = None
        
        # self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        # self.setStyleSheet("background-color: #666666;")
        # self.setStyleSheet("QWidget { background: #666666; }")

        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.red)
        self.setPalette(p)
        
        self.info_widget = QWidget()
        self.info_widget.setStyleSheet("background-color: #333333; color: #CCCCCC;")
        self.setStyleSheet("background-color: #333333; color: #CCCCCC;")
        
        self.main_layout = QVBoxLayout()
        SetSpacing(self.main_layout, 0)
        
        self.setLayout(self.main_layout)

        self.info_edit = InfoEdit(self)
        self.info_widget.setLayout(self.info_edit)
        self.main_layout.addWidget(self.info_widget)
        
        # self.show()
    
    def SetInfo(self, car_config):
        self.car_config = car_config
        self.info_edit.Reset()
        
        self.info_edit.AddLineEdit("car", car_config)


def SetSpacing(widget, spacing):
    widget.setSpacing(spacing)
    widget.setContentsMargins(QMargins(spacing, spacing, spacing, spacing))


class Listing(BaseCategory):
    def __init__(self, parent):
        super().__init__(parent, "Listing", "listing")
        self._parent = parent
        self.info_edit = InfoEdit(self)
        self.info_layout.addLayout(self.info_edit)
    
    def SetInfo(self, car_config):
        self.Reset(car_config)
        self.info_edit.Reset()
        
        self.info_edit.AddLineEdit("url")
        self.info_edit.AddLineEdit("location")
        self.info_edit.AddLineEdit("price")
        self.info_edit.AddLineEdit("date_posted")
        self.info_edit.AddButton("sold", ("true", "false"))
        self.info_edit.AddTextEdit("description")


class Engine(BaseCategory):
    def __init__(self, parent):
        super().__init__(parent, "Engine", "engine")
        self._parent = parent
        self.info_edit = InfoEdit(self)
        self.info_layout.addLayout(self.info_edit)
    
    def SetInfo(self, car_config):
        self.Reset(car_config)
        try:
            self.info_edit.Reset()
            
            self.info_edit.AddButton("transmission", ("Automatic", "Manual"))
            self.info_edit.AddLineEdit("gears")
            self.info_edit.AddLineEdit("miles")
            self.info_edit.AddLineEdit("horsepower")
            self.info_edit.AddLineEdit("torque")
            self.info_edit.AddLineEdit("cylinders")
            self.info_edit.AddLineEdit("liter")
            self.info_edit.AddLineEdit("valves")
        except Exception as F:
            print(str(F))


class CarInfo(BaseCategory):
    def __init__(self, parent):
        super().__init__(parent, "Car Info", "car_info")
        self._parent = parent
        self.info_edit = InfoEdit(self)
        self.info_layout.addLayout(self.info_edit)
    
    def SetInfo(self, car_config):
        self.Reset(car_config)
        self.info_edit.Reset()
        
        self.info_edit.AddLineEdit("exterior")
        self.info_edit.AddLineEdit("interior")
        self.info_edit.AddLineEdit("condition")
        self.info_edit.AddLineEdit("air_bags")
        self.info_edit.AddLineEdit("seating")


class MilesPerGallon(BaseCategory):
    def __init__(self, parent):
        super().__init__(parent, "Miles Per Gallon", "mpg")
        self._parent = parent
        self.info_edit = InfoEdit(self)
        self.info_layout.addLayout(self.info_edit)
    
    def SetInfo(self, car_config):
        self.Reset(car_config)
        self.info_edit.Reset()
        
        self.info_edit.AddLineEdit("city")
        self.info_edit.AddLineEdit("highway")
        self.info_edit.AddLineEdit("combined")





