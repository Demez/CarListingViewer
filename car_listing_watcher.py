# ============================================================
# some dumb program to record car listings
# first actual GUI i setup, so it might be shit
#
# needed modules:
# pip install pyqt5 hjson beautifulsoup
# ============================================================

import argparse
import sys

import demez_key_values.demez_key_values as dkv

from car_edit_ui import CarAddUI
from car_info_ui import CarInfoUI
from image_viewer import ImageViewer
from dir_tools import CreateDirectory
from shared import (CreateCarObject, BackupConfig,
                    MAIN_FONT, BUTTON_CSS,
                    CAR_NAME_HEADER_COLOR, LIST_INFO_BG_COLOR, FONT_COLOR, BUTTON_COLOR, BUTTON_COLOR_PRESSED,
                    FONT_SIZE_LARGE, FONT_SIZE_MED, FONT_SIZE_SMALL,
                    FONT_SIZE_HEADER_LARGE, FONT_SIZE_HEADER_MED, FONT_SIZE_HEADER_SMALL)

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


def ParseArgs():
    cmd_parser = argparse.ArgumentParser()
    cmd_parser.add_argument("--config", "-c", required=True, help="Config file containing all cars")
    return cmd_parser.parse_args()


# oh god, hacky sliding widget with using a QSlider and use it's position
# http://zetcode.com/gui/pyqt5/customwidgets/


class CarWatcherGUI(QWidget):
    def __init__(self, config, car_list):
        super().__init__()
        self._config = config
        self.main_layout = QHBoxLayout()
        
        self.car_list = []
        self.car_list_items = []
        self.car_list_ui = QListWidget()
        self.update_all_btn = QPushButton("Update All")
        self.remove_btn = QPushButton("Remove Car")
        
        self.car_add_ui = CarAddUI(self)

        self.center_layout = QVBoxLayout()
        self.image_viewer_widget = QLabel()
        self.image_viewer = ImageViewer(self.image_viewer_widget)
        self.image_list_ui = QListWidget()
        
        # self.car_image_widget = QWidget()
        self.current_car = QLabel()
        # self.image_preview_new = QGraphicsView()
        # self.image_preview = QLabel()
        
        self.car_info_ui = CarInfoUI(self)
        
        # maybe temporary
        self._current_image = 0
        
        self.InitUI(car_list)
    
    def InitUI(self, car_list):
        self.setWindowTitle('fuck')
        self.setFocusPolicy(Qt.StrongFocus)
        # relative to top left corner
        # x, y, width, height
        self.setGeometry(0, 0, 1680, 800)

        # center window
        qt_rectangle = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        qt_rectangle.moveCenter(center_point)
        self.move(qt_rectangle.topLeft())
        
        self.setLayout(self.main_layout)
        # self.showMaximized()

        # LIST_INFO_BG_COLOR
        # set to 2px for debugging, 0px by default
        self.setStyleSheet(f"""
            border: 0px solid;
            border-color: #0099ff;
            background-color: {LIST_INFO_BG_COLOR};
            color: {FONT_COLOR};
            outline: 0; {BUTTON_CSS};
        """)

        self.image_viewer.setGeometry(0, 0, 960, 720)

        self.CreateCarListUI(car_list)
        
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(QMargins(0, 0, 0, 0))
        self.main_layout.addLayout(self.center_layout)
        self.main_layout.addLayout(self.car_info_ui)
        
        self.current_car.setAlignment(Qt.AlignCenter)
        self.current_car.setFixedHeight(64)
        self.current_car.setFont(QFont(MAIN_FONT, FONT_SIZE_HEADER_LARGE))
        self.current_car.setStyleSheet(f"QLabel {{ padding: 12px; background-color: {CAR_NAME_HEADER_COLOR};}}")
        
        self.center_layout.setSpacing(0)
        self.center_layout.addWidget(self.current_car)
        self.center_layout.addWidget(self.image_viewer)

        current_car_frame = self.current_car.frameGeometry()
        self.image_viewer.setGeometry(0, 0, current_car_frame.width(),
                                      qt_rectangle.height() - current_car_frame.height())
        
        # select the first one by default
        if car_list:
            self.car_list_ui.setCurrentRow(0)
            self.OnCarClick()

        self.show()

    def CreateCarListUI(self, car_list):
        self.car_list_ui.setFont(QFont(MAIN_FONT, FONT_SIZE_SMALL))
        self.car_list_ui.setWordWrap(True)
        self.car_list_ui.setSpacing(2)  # 4
        # self.car_list_ui.setFixedWidth(308)  # 288
        self.car_list_ui.setMaximumWidth(340)
        self.car_list_ui.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.car_list_ui.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.car_list_ui.itemSelectionChanged.connect(self.OnCarClick)
        self.car_list_ui.setStyleSheet(
            f"""
            QListWidget:item:selected:active {{
                 background: {BUTTON_COLOR};
            }}
            QListWidget:item:selected:!active {{
                 background: {BUTTON_COLOR};
            }}
            QListWidget:item:selected:disabled {{
                 background: {BUTTON_COLOR};
            }}
            QListWidget:item:selected:!disabled {{
                 background: {BUTTON_COLOR};
            }}
            QListWidget:item:hover {{
                 background: {BUTTON_COLOR_PRESSED};
            }}
            QListWidget:item {{
                 color: #CCCCCC;
                 padding: 4px;
                 border: 0px;
            }}
            """
        )

        label = QLabel("Car List")
        label.setFixedHeight(32)
        label.setFont(QFont(MAIN_FONT, FONT_SIZE_LARGE))
        label.setAlignment(Qt.AlignCenter)

        add_car_btn = QPushButton("Add Car", self)
        add_car_btn.setToolTip("Enter the url of a listing to automatically add it")
        add_car_btn.setFixedHeight(32)
        add_car_btn.setStyleSheet(BUTTON_CSS)
        add_car_btn.setFont(QFont(MAIN_FONT, FONT_SIZE_SMALL))
        add_car_btn.clicked.connect(self.OnAddCarBtnClick)

        self.update_all_btn.setToolTip("Update all cars from the URL")
        self.update_all_btn.setFixedHeight(32)
        self.update_all_btn.setStyleSheet(BUTTON_CSS)
        self.update_all_btn.setFont(QFont(MAIN_FONT, FONT_SIZE_SMALL))
        self.update_all_btn.clicked.connect(self.UpdateAllBtn)
        self.update_all_btn.hide()

        self.remove_btn.setToolTip("Remove the currently selected car")
        self.remove_btn.setFixedHeight(32)
        self.remove_btn.setStyleSheet(BUTTON_CSS)
        self.remove_btn.setFont(QFont(MAIN_FONT, FONT_SIZE_SMALL))
        self.remove_btn.clicked.connect(self.OnRemoveCarBtnPress)
        self.remove_btn.hide()
        
        car_list_layout = QVBoxLayout()
        car_list_layout.addWidget(label)
        car_list_layout.addWidget(self.car_list_ui)
        car_list_layout.addWidget(self.update_all_btn)
        car_list_layout.addWidget(self.remove_btn)
        car_list_layout.addWidget(add_car_btn)
        car_list_layout.setSpacing(8)
        car_list_layout.setContentsMargins(QMargins(8, 8, 8, 8))
        
        self.main_layout.addLayout(car_list_layout)

        for car_obj in car_list:
            self.AddCar(car_obj)

    def UpdateImagePreview(self, image):
        if self.image_viewer.setPhoto(image):
            return True
        else:
            self.image_viewer.removePhoto()
            return False

    def SetCarImage(self, parsed_car):
        self._current_image = 0
        if parsed_car.images:
            car_image_list = GetAllKeysInDKVList(parsed_car.images)
            if car_image_list:
                for image in car_image_list:
                    if self.image_viewer.setPhoto(image):
                        break
                else:
                    self.image_viewer.removePhoto()
        else:
            self.image_viewer.removePhoto()
            
    def DisplayCarImageSelectionList(self, car_image_list):
        pass
        
    def DisplayCarInfo(self, parsed_car):
        self.car_info_ui.current_car = self.GetCurrentCar()
        self.car_info_ui.edit_car.show()
        self.car_info_ui.listing.SetInfo(parsed_car.listing)
        self.car_info_ui.engine.SetInfo(parsed_car.engine)
        self.car_info_ui.car.SetInfo(parsed_car.car_info)
        self.car_info_ui.mpg.SetInfo(parsed_car.mpg)
    
    def AddCar(self, car_obj):
        car_name = car_obj.GetItemValue("car")
        car_id = car_obj.GetItemValue("id")
        
        if not car_name:
            car_obj.FatalError("Need to have a \"car\" attribute")
            
        car_list_item = QListWidgetItem(car_name)
        self.car_list_ui.addItem(car_list_item)
        self.car_list_items.append(car_list_item)

        if not car_id or int(car_id) < 0:
            car_obj.GetItem("id").value = str(len(self.car_list))
            self.car_list.append(car_obj)
        else:
            self.car_list.insert(int(car_id), car_obj)
    
    def RemoveCar(self, index: int):
        self.car_list_ui.takeItem(index)
        self.car_list_ui.update()
        self.car_list.remove(self.car_list[index])
    
    def RemoveCarByDKV(self, car_obj: dkv.DemezKeyValue):
        index = self.car_list.index(car_obj)
        self.RemoveCar(index)
        
    def GetCurrentCar(self):
        car_id = self.car_list_ui.currentRow()
        car_obj = self.car_list[car_id]
        return car_obj
        
    def GetCurrentImage(self):
        image_id = self._current_image
        image_list = self.GetImageList()
        if image_list:
            return image_list[image_id]
        return None
        
    def GetImageList(self):
        car_obj = self.GetCurrentCar()
        parsed_car = CreateCarObject(car_obj)
        if parsed_car.images:
            return GetAllKeysInDKVList(parsed_car.images)
        return []
    
    def AddToConfig(self, dkv_root):
        BackupConfig(args.config)
        self._config.value.extend(dkv_root.value)
        config_str = self._config.ToString(indent=1)
        with open(args.config, "w", encoding="utf-8") as test_file:
            test_file.write(config_str)
    
    def NewConfig(self, new_config):
        BackupConfig(args.config)
        self._config = new_config
        config_str = self._config.ToString(indent=1)
        with open(args.config, "w", encoding="utf-8") as test_file:
            test_file.write(config_str)
        self.OnCarClick()
    
    def WriteConfig(self):
        BackupConfig(args.config)
        config_str = self._config.ToString(indent=1)
        with open(args.config, "w", encoding="utf-8") as test_file:
            test_file.write(config_str)
        self.UpdateCurrentCarName()

        car_obj = self.GetCurrentCar()
        parsed_car = CreateCarObject(car_obj)
        self.DisplayCarInfo(parsed_car)
        self.current_car.setText(parsed_car.car)
        self.remove_btn.show()
        self.update_all_btn.show()

        if not self.car_info_ui.car_edit_ui.isHidden():
            self.car_info_ui.OnEditInfoBtnClick()
        
    def UpdateCurrentCarName(self):
        row = self.car_list_ui.currentRow()
        car_obj = self.car_list[row]
        car_list_item = self.car_list_items[row]

        car_name = car_obj.GetItemValue("car")
        car_list_item.setText(car_name)
    
    def ReloadConfig(self):
        return
    
    def keyPressEvent(self, event: QKeyEvent):
        current_row = self.car_list_ui.currentRow()
        last_row = len(self.car_list_ui) - 1
        
        if event.key() == Qt.Key_Up:
            if current_row != 0:
                self.car_list_ui.setCurrentRow(current_row - 1)
            else:
                self.car_list_ui.setCurrentRow(last_row)
                
        elif event.key() == Qt.Key_Down:
            if current_row != last_row:
                self.car_list_ui.setCurrentRow(current_row + 1)
            else:
                self.car_list_ui.setCurrentRow(0)
                
        else:
            self.image_viewer.keyPressEvent(event)

    # TODO: somehow store the selected image for this car,
    #  so if we switch back to this, it stays on the same image
    @pyqtSlot()
    def OnCarClick(self):
        car_obj = self.GetCurrentCar()
        parsed_car = CreateCarObject(car_obj)
        self.DisplayCarInfo(parsed_car)
        self.SetCarImage(parsed_car)
        self.current_car.setText(parsed_car.car)
        self.remove_btn.show()
        self.update_all_btn.show()
        
        if not self.car_info_ui.car_edit_ui.isHidden():
            self.car_info_ui.OnEditInfoBtnClick()

    @pyqtSlot()
    def UpdateAllBtn(self):
        for item in self.car_list:
            self.car_info_ui.car_edit_ui.UpdateInfo(item)
            self.car_info_ui.car_edit_ui.OnUpdateBtnPress()

    @pyqtSlot()
    def OnImageClick(self):
        self.UpdateImagePreview(self.GetCurrentImage())

    @pyqtSlot()
    def OnAddCarBtnClick(self):
        self.car_add_ui.show()
        # self.car_add_ui.raise_()
        self.car_add_ui.activateWindow()

    @pyqtSlot()
    def OnRemoveCarBtnPress(self):
        index = self.car_list_ui.currentRow()
        car_obj = self.GetCurrentCar()
        car_obj.Delete()

        try:
            # reload the config pretty much
            self.WriteConfig()
            self.remove_btn.hide()
        
            self.RemoveCar(index)

            # select the one before or after it, or none if none are available
            if index > 0:
                self.car_list_ui.setCurrentRow(index - 1)
                self.OnCarClick()
            elif index == 0 and len(self.car_list) > 0:
                self.car_list_ui.setCurrentRow(0)
                self.OnCarClick()
            else:
                self.remove_btn.hide()
    
                self.car_info_ui.listing.hide()
                self.car_info_ui.engine.hide()
                self.car_info_ui.car.hide()
                self.car_info_ui.mpg.hide()
                self.car_info_ui.edit_car.hide()
                
                self.current_car.setText("")
                
                self.image_viewer.removePhoto()
                print("what")
                
        except Exception as F:
            print(str(F))


def GetAllKeysInDKVList(dkv_list):
    keys = []
    [keys.append(value.key) for value in dkv_list]
    return keys


def StartGUI(config, car_list):
    try:
        app = QApplication(sys.argv)
        app.setStyleSheet("border: 0px")
        gui = CarWatcherGUI(config, car_list)
        
        # must be called at the end
        sys.exit(app.exec_())
        
    except Exception as F:
        print(str(F))


def GetCarsInConfig():
    config = dkv.ReadFile(args.config)
    car_list = []
    for obj in config:
        if obj.key == "car":
            car_list.append(obj)
        else:
            obj.Unknown()
    return config, car_list


def main():
    CreateDirectory("images")
    config, car_list = GetCarsInConfig()
    StartGUI(config, car_list)


if __name__ == "__main__":
    args = ParseArgs()
    INFO_WIDTH = 448
    main()
