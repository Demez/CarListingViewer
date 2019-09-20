
from bs4 import BeautifulSoup
from demez_key_values.demez_key_values import FromDict
import hjson
import re
import urllib.request
from datetime import datetime

ENGINE_FEATURES = {"V8, 4.6 Liter", "Dual Air Bags", "Automatic", "Manual, 5-Spd", "Leather"}


def GrabListingRenderable(text):
    try:
        listing_renderable_start = "listingRenderable:{" + text.split("listingRenderable:{")[1]
    except IndexError:
        print("Product is probably unavailable")
        return
    except Exception as F:
        print(str(F))
        return
    
    # now go through and try to find the end correctly
    depth = 1
    listing_renderable = ""
    for index, char in enumerate(listing_renderable_start):
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            
        if depth == 0:
            break
        else:
            listing_renderable += char

    try:
        result = hjson.loads(listing_renderable.split("listingRenderable:", 1)[1])
        dict_result = ConvertOrderedDictToDict({}, result)
        return dict_result
    except Exception as F:
        print(str(F))
        return
        

def ConvertOrderedDictToDict(new_dict, ordered_dict):
    try:
        for key, value in ordered_dict.items():
            if type(value) in {str, int, float, dict, bool, type(None)}:
                new_dict[key] = value
            elif type(value) == list:
                new_dict[key] = []
                for ordered_dict_item in value:
                    if type(ordered_dict_item) not in {str, int, float, dict, bool, type(None)}:
                        new_dict[key].append(ConvertOrderedDictToDict({}, ordered_dict_item))
                    else:
                        new_dict[key].append(ordered_dict_item)
            else:
                new_dict[key] = ConvertOrderedDictToDict({}, value)
    except Exception as F:
        print(str(F))
        
    return new_dict


def MakeCarDictFromDict(dct, url):
    car_dict = {"id": "-1"}
    
    _CarName(car_dict, dct)
    _Listing(car_dict, dct, url)

    if "serialized_verticals_data" in dct:
        car_info_ordered = hjson.loads(dct["serialized_verticals_data"])
        car_info = ConvertOrderedDictToDict({}, car_info_ordered)
        dct["serialized_verticals_data"] = car_info

        engine_features = _CarInfoDict(car_dict, car_info)
        _EngineDict(car_dict, car_info, engine_features)
        _GasMileageDict(car_dict, car_info)
        
    _ImagesDict(car_dict, dct)
    
    return car_dict


def _CarName(root_dct, dct):
    if "custom_title" in dct and dct["custom_title"]:
        root_dct["car"] = dct["custom_title"]
    elif "marketplace_listing_title" in dct and dct["marketplace_listing_title"]:
        root_dct["car"] = dct["marketplace_listing_title"]
    else:
        root_dct["car"] = "Unknown"
        

def _Listing(root_dct, dct, url):
    listing_dict = {"url": url}
    
    if "redacted_description" in dct:
        listing_dict["description"] = dct["redacted_description"]["text"]
    
    if "location" in dct:
        listing_dict["location"] = dct["location"]["reverse_geocode"]["city"] + ", " + \
                                   dct["location"]["reverse_geocode"]["state"]
    
    if "is_sold" in dct:
        listing_dict["sold"] = str(dct["is_sold"]).casefold()
        
    # if "formatted_price" in dct:
    #     listing_dict["price"] = dct["formatted_price"]["text"]
    
    if "item_price" in dct:
        price = str(dct["item_price"]["offset_amount"])
        price = price[:-2] + "." + price[-2:]
        listing_dict["price"] = price
        
    if "creation_time" in dct:
        listing_dict["date_posted"] = str(datetime.fromtimestamp(dct["creation_time"]))
            
    if listing_dict:
        root_dct["listing"] = listing_dict


def _CarInfoDict(root_dct, dct):
    info_dict = {}

    __AddDictOption("exterior", "exteriorColor", info_dict, dct)
    __AddDictOption("interior", "interiorColor", info_dict, dct)
    __AddDictOption("condition", "vehicleCondition", info_dict, dct)
    
    engine_features = __AddVehicleFeatures(info_dict, dct)
    
    if "Dual Air Bags" in engine_features:
        info_dict["air_bags"] = "2"
        
    if "Leather" in engine_features:
        info_dict["seating"] = "Leather"
        
    if info_dict:
        root_dct["car_info"] = info_dict
        
    return engine_features


def _EngineDict(root_dct, dct, engine_features):
    info_dict = {}

    __AddDictOption("miles", "mileage", info_dict, dct)
    
    if "Automatic" in engine_features and "Manual, 5-Spd" in engine_features:
        info_dict["transmission"] = ""
    elif "Automatic" in engine_features:
        info_dict["transmission"] = "Automatic"
    elif "Manual, 5-Spd" in engine_features:
        info_dict["transmission"] = "Manual"
        info_dict["gears"] = "5"
    
    if "isManualTransmission" in dct:
        if dct["isManualTransmission"]:
            info_dict["transmission"] = "Manual"
        else:
            info_dict["transmission"] = "Automatic"
            
    if "V8, 4.6 Liter" in engine_features:
        info_dict["cylinders"] = "8"
        info_dict["liter"] = "4.6"
    
    if info_dict:
        root_dct["engine"] = info_dict


def _GasMileageDict(root_dct, dct):
    info_dict = {}
    
    if "vehicleSpecifications" in dct:
        spec_dct = dct["vehicleSpecifications"]
        __AddDictOption("city", "Value", info_dict, spec_dct["GasMileageCity"])
        __AddDictOption("highway", "Value", info_dict, spec_dct["GasMileageHighway"])
        __AddDictOption("combined", "Value", info_dict, spec_dct["GasMileageCombined"])
    
    if info_dict:
        root_dct["mpg"] = info_dict
            
        
def __AddListOption(dkv_list: list, lst: list, item):
    if item in lst:
        dkv_list.append(item)
        
        
def __AddDictOption(dkv_key, key, dkv_dict, dct):
    try:
        dkv_dict[dkv_key] = dct[key]
    except KeyError:
        pass
    except TypeError:
        pass
        
        
def __AddVehicleFeatures(dkv_dict, dct):
    other_features = set([])
    
    if "vehicleFeatures" in dct:
        dkv_dict["features"] = set([])
        for feature_dict in dct["vehicleFeatures"]:
            
            if feature_dict["DisplayName"] not in ENGINE_FEATURES:
                dkv_dict["features"].add(feature_dict["DisplayName"])
            else:
                other_features.add(feature_dict["DisplayName"])
                
        dkv_dict["features"] = sorted(list(dkv_dict["features"]))
        
    return other_features
        

def _ImagesDict(root_dct, dct):
    if "listing_photos" in dct:
        root_dct["images"] = []
        for photo in dct["listing_photos"]:
            root_dct["images"].append(photo["image"]["uri"])


def OpenURL(url):
    try:
        web_source = urllib.request.urlopen(url)
        soup = BeautifulSoup(web_source.read(), "html.parser")
        facebook_fucking_sucks = GrabListingRenderable(soup.text)
        
        car_dict = MakeCarDictFromDict(facebook_fucking_sucks, url)
        
        root_dkv = FromDict({"car": car_dict})
        
        return root_dkv
    
    except Exception as F:
        print(str(F))
