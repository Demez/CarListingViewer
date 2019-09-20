import re
import urllib.request
import urllib.parse

import facebook_marketplace_listing as facebook


# Image formats supported by Qt
VALID_FORMAT = ('.BMP', '.GIF', '.JPG', '.JPEG', '.PNG', '.PBM', '.PGM', '.PPM', '.TIFF', '.XBM')

# source: https://stackoverflow.com/questions/7160737/python-how-to-validate-a-url-in-python-malformed-or-not
DOMAIN_FORMAT = re.compile(
    r"(?:^(\w{1,255}):(.{1,255})@|^)"  # http basic authentication [optional]
    r"(?:(?:(?=\S{0,253}(?:$|:))"  # check full domain length to be less than or equal to 253 (starting after http basic auth, stopping before port)
    r"((?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+"  # check for at least one subdomain (maximum length per subdomain: 63 characters), dashes in between allowed
    r"(?:[a-z0-9]{1,63})))"  # check for top level domain, no dashes allowed
    r"|localhost)"  # accept also "localhost" only
    r"(:\d{1,5})?",  # port [optional]
    re.IGNORECASE
)

SCHEME_FORMAT = re.compile(
    r"^(http|hxxp|ftp|fxp)s?$",  # scheme: http(s) or ftp(s)
    re.IGNORECASE
)


def MakeCarDKVFromURL(url):
    if not IsValidUrl(url):
        print("Not a Valid URL")
        return
    
    if "facebook.com/marketplace" in url:
        car_dkv = facebook.OpenURL(url)
        return car_dkv
    
    print("uhhhhhhhhh")


# source: https://stackoverflow.com/questions/7160737/python-how-to-validate-a-url-in-python-malformed-or-not
# idk if checking if it's a path would be better or not
def IsValidUrl(url: str):
    if len(url) > 2048:
        raise Exception("URL exceeds its maximum length of 2048 characters (given length={})".format(len(url)))

    result = urllib.parse.urlparse(url)
    scheme = result.scheme
    domain = result.netloc

    if not scheme or not domain or not re.fullmatch(SCHEME_FORMAT, scheme) or not re.fullmatch(DOMAIN_FORMAT, domain):
        return False

    return True
