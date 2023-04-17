import requests
from arcgis.gis import GIS
from arcgis.mapping import WebMap

PORTAL_URL = "https://bcgov03.maps.arcgis.com"
PORTAL_USERNAME = os.getenv('GEOHUB_USERNAME')
PORTAL_PASSWORD = os.environ.get('GEOHUB_PASSWORD')

gis = GIS(PORTAL_URL, username=PORTAL_USERNAME, password=PORTAL_PASSWORD, expiration=9999)

mapitem = gis.content.get("315a1d9eb33c49b59bfbefae157eaef3")

wm = WebMap(mapitem)

for layer in wm.layers:
    url = f'{layer.url}?f=json'
    x = requests.get(url)
    print(url)
    if x.status_code == 200:
        if "error" in x.json():
            print("Shit")
        else:
            print("Good")
    else:
        print(x.status_code)
