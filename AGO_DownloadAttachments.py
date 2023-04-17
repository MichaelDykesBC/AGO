import pandas as pd
from arcgis.gis import GIS

filelocation = r'C:\Users\Mike\Desktop\COP2022_Photos'

PORTAL_URL = "https://bcgov03.maps.arcgis.com"
PORTAL_USERNAME = os.getenv('GEOHUB_USERNAME')
PORTAL_PASSWORD = os.environ.get('GEOHUB_PASSWORD')
gis = GIS(PORTAL_URL, username=PORTAL_USERNAME, password=PORTAL_PASSWORD, expiration=9999)

itemid = "6076b41e1dfd42b19e408a247640abf6"

layer_item = gis.content.get(itemid)
layer_lyr = layer_item.layers[0]

attachments = layer_lyr.export_attachments(filelocation)

sdf = pd.DataFrame.spatial.from_layer(layer_lyr)
sdf.to_excel(r'C:\Users\Mike\Desktop\COP2022_Photos\COP2022_WhiteboardResults.xlsx', index=False)