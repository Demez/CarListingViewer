
from os import path, sep
from dir_tools import CopyFile
import enum

from PyQt5.QtWidgets import *
# from PyQt5.QtGui import *
# from PyQt5.QtCore import *


# MAIN_FONT = "SansSerif"
MAIN_FONT = "Meiryo UI"

FONT_SIZE_HEADER_LARGE = 20
FONT_SIZE_HEADER_MED = 18
FONT_SIZE_HEADER_SMALL = 16

FONT_SIZE_LARGE = 14
FONT_SIZE_MED = 12
FONT_SIZE_SMALL = 10

FONT_COLOR = "#CCCCCC"

BUTTON_COLOR_HOVER = "#595959"
BUTTON_COLOR_PRESSED = "#333333"
BUTTON_COLOR = "#444444"

INFO_TITLE_COLOR_HOVER = "#808080"
INFO_TITLE_COLOR_PRESSED = "#4d4d4d"
INFO_TITLE_COLOR = "#666666"

# TABLE_COLOR = "#666666"
INFO_BOX_COLOR = "#444444"
LIST_INFO_BG_COLOR = "#222222"

CAR_NAME_HEADER_COLOR = "#333333"

BUTTON_CSS = f"""
QPushButton         {{ background-color: {BUTTON_COLOR}; }}
QPushButton:hover   {{ background-color: {BUTTON_COLOR_HOVER} }}
QPushButton:pressed {{ background-color: {BUTTON_COLOR_PRESSED} }}
"""


def CreateCarObject(car_cfg):
    try:
        car_obj = Car()
        for cfg_value in car_cfg.value:
            car_obj.AddDKVOption(cfg_value)
        return car_obj
    except Exception as F:
        print(str(F))
        
        
def CenterWindow(widget):
    qt_rectangle = widget.frameGeometry()
    center_point = QDesktopWidget().availableGeometry().center()
    qt_rectangle.moveCenter(center_point)
    widget.move(qt_rectangle.topLeft())


def BackupConfig(config):
    file_folder, file_name = path.split(config)
    if file_folder:
        new_folder = file_folder + sep + "backups" + sep
    else:
        new_folder = "backups" + sep
    new_base_name = new_folder + file_name + "_backup"
    
    index = 0
    while True:
        new_name = new_base_name + str(index)
        if path.isfile(new_name):
            index += 1
            continue
        break
    
    CopyFile(config, new_name)


class BaseListing:
    def AddDKVOption(self, dkv_obj):
        if dkv_obj.key in self.__dict__:
            key_type = type(self.__dict__[dkv_obj.key])
            
            if key_type in {str, int, float}:
                try:
                    converted_value = key_type(dkv_obj.value)
                except ValueError:
                    converted_value = key_type(0)
                except Exception as F:
                    print(str(F))
                    return
            
            elif key_type == bool:
                if dkv_obj.value.casefold() == "true":
                    converted_value = True
                elif dkv_obj.value.casefold() == "false":
                    converted_value = False
                else:
                    dkv_obj.InvalidOption("true", "false")
                    return
            
            elif key_type == list:
                converted_value = []
                for item in dkv_obj.value:
                    converted_value.append(item)
            
            else:
                converted_value = self.__dict__[dkv_obj.key]
                for item in dkv_obj.value:
                    converted_value.AddDKVOption(item)
            
            self.__dict__.update({dkv_obj.key: converted_value})
        else:
            dkv_obj.Unknown()
            
    def HasValues(self):
        for key, value in self.__dict__.items():
            if type(value) in {str, int, float, list, bool}:
                if value:
                    return True
            else:
                print("unknown value type")
        return False


class Car(BaseListing):
    def __init__(self):
        self.id = 0
        self.car = ""
        
        self.listing = Listing()
        self.engine = Engine()
        self.mpg = MilesPerGallon()
        self.car_info = CarInfo()
        
        self.images = []
        self.other = []


# TODO: maybe add these things:
#  - view count
#  - kelly blue book stuff
class Listing(BaseListing):
    def __init__(self):
        self.url = ""
        self.description = ""
        self.location = ""
        self.price = 0.0
        self.date_posted = ""
        self.sold = False


class Engine(BaseListing):
    def __init__(self):
        self.transmission = ""
        self.gears = 0
        self.miles = 0
        self.horsepower = 0
        self.torque = 0
        self.cylinders = 0
        self.liter = 0.0
        self.valves = 0


class MilesPerGallon(BaseListing):
    def __init__(self):
        self.city = 0.0
        self.highway = 0.0
        self.combined = 0.0


# TODO: maybe add some of the vehicle dimensions here?
class CarInfo(BaseListing):
    def __init__(self):
        self.exterior = ""
        self.interior = ""
        self.condition = ""
        self.radio = ""
        self.seating = ""
        self.air_bags = 0
        
        self.features = []
        
        
        '''self.url = ""
        self.description = ""
        self.location = ""
        self.price = 0.0
        self.date_posted = ""
        self.sold = False'''
        
        
KEY_TO_DISPLAY_NAMES = {
    # "mpg": "Miles Per Gallon",
    
    "car": "Car Name",
    
    "url": "URL",
    "description": "Description",
    "location": "Location",
    "price": "Price",
    "date_posted": "Date Posted",
    "sold": "Sold",
    
    "transmission": "Transmission",
    "gears": "Gears",
    "miles": "Miles",
    "horsepower": "Horsepower",
    "torque": "Torque",
    "cylinders": "Cylinders",
    "liter": "Liter",
    "valves": "Valves",
    
    "city": "City",
    "highway": "Highway",
    "combined": "Combined",
    
    "exterior": "Exterior",
    "interior": "Interior",
    "condition": "Condition",
    "radio": "Radio",
    "seating": "Seating",
    "air_bags": "Air Bags",
    "features": "Features",
}


def GetDisplayName(key):
    try:
        return KEY_TO_DISPLAY_NAMES[key]
    except KeyError:
        return key


def DeleteEntireLayout(layout):
    for i in reversed(range(layout.count())):
        item = layout.itemAt(i)
        
        if item.layout():
            sub_layout = item.layout()
            sub_layout.setParent(None)
            sub_layout.deleteLater()
            DeleteEntireLayout(sub_layout)
        
        elif item.widget():
            widget = item.widget()
            layout.removeWidget(widget)
            widget.setParent(None)
            widget.deleteLater()
            widget = None
        item = None
        
    
def NumberFormat(number):
    if type(number) == int:
        return "{:,}".format(number)
    elif type(number) == float:
        return "{:,.2f}".format(number)
    else:
        return number

