###==================================================================================================================================================
###     BC Weather Alerts ECCC
###     (BC_Weather_Alerts_ECCC.py)
###
###     Written by: Michael Dykes (michael.dykes@gov.bc.ca)
###
###     Created: June 23 2022
###     Edited: August 18 2022 (MDykes)
###
###     Purpose: Get BC Weather Alerts from ECCC website GeoJSON and update hosted feature layer in GeoHub
###==================================================================================================================================================
# Import libraries/modules
import sys, json, requests, datetime, logging
from arcgis.gis import GIS
from arcgis import geometry, features
from datetime import datetime, timezone

# Create logger and set logging level (NOTSET,DEBUG,INFO,WARNING,ERROR,CRITICAL)
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("my-logger")

# Load config file to get AGO parameter values
config_file = sys.argv[1]
with open(config_file) as json_conf : 
    CONF = json.load(json_conf)

# BC GeoHub parameters and credentials needed for connection
PORTAL_URL = CONF["AGO_Portal_URL"]
PORTAL_USERNAME = sys.argv[2]
PORTAL_PASSWORD = sys.argv[3]

# Get ItemID parameters from config file and assign to varaiables
WeatherAlerts_ItemID = CONF["WeatherAlerts_ItemID"]
SitRepDashboard_ItemID = CONF["SitRepDashboard_ItemID"]

# URL to connect to the GEOJSON from ECCC Weather Alerts (Filtered down to BC only) and use request module to connect to website data
url = r"https://geo.weather.gc.ca/geomet?lang=en&SERVICE=WFS&REQUEST=GetFeature&layer=ALERTS&version=2.0.0&typenames=ALERTS&outputformat=application/json;%20subtype=geojson&filter=<ogc:Filter><ogc:PropertyIsLike%20wildCard='*'%20singleChar='.'%20escape='!'><ogc:PropertyName>identifier</ogc:PropertyName><ogc:Literal>*CWVR08*</ogc:Literal></ogc:PropertyIsLike></ogc:Filter>"
x = requests.get(url)

def Update_Weather_Alerts():
    # If good web return/connection
    if x.status_code == 200:
        # If data that can be read in json is returned
        if x and x.json():
            log.info(f"{len(x.json()['features'])} BC Weather Alerts")
            # Attempt to connect to AGO and update the hosted feature layer
            attempts = 0
            success = False
            # 5 attempts to connect and update the layer 
            while attempts < 5 and not success:
                try:
                    # Connect to GIS portal
                    gis = GIS(PORTAL_URL, username=PORTAL_USERNAME, password=PORTAL_PASSWORD, expiration=9999)
                    # Get Hosted Feature Layer to Update
                    HFS_item = gis.content.get(WeatherAlerts_ItemID)
                    # Delete all existing feature layer features and reset OBJECTID/FID counter
                    HFS_item.layers[0].delete_features(where="objectid >= 0")
                    HFS_item.layers[0].manager.truncate()

                    # Iterate through rows in ECCC Weather Alerts JSON
                    for row in x.json()['features']:
                        if row['properties']['area']:
                            # Create arcgis geometry object from GEOJSON
                            geom = geometry.Geometry(row['geometry'])

                            # Figure out sorting field for alert_type:
                            Alert_Type_Sort_Dict = {"warning":0,"watch":1,"statement":2,"advisory":3}

                            # Align attributes from AGO fields names to attributes from the GEOJSON
                            attributes = {"identifier":row['properties']['identifier'], 
                                    "area":row['properties']['area'],
                                    "headline":row['properties']['headline'],
                                    "status":row['properties']['status'],
                                    "alert_type":row['properties']['alert_type'],
                                    "descrip_en":row['properties']['descrip_en'],
                                    "effective": datetime.strptime(row['properties']['effective'],"%Y/%m/%d  %H:%M:%S+00").replace(tzinfo=timezone.utc).astimezone(tz=None) if row['properties']['effective'] else None,
                                    "expires": datetime.strptime(row['properties']['expires'],"%Y/%m/%d  %H:%M:%S+00").replace(tzinfo=timezone.utc).astimezone(tz=None) if row['properties']['expires'] else None,
                                    "sort":Alert_Type_Sort_Dict[row['properties']['alert_type']]}
                            log.debug(attributes)
                            # Create new feature
                            newfeature = features.Feature(geom,attributes)
                            # Add feature to existing hosted feature layer
                            result = HFS_item.layers[0].edit_features(adds = [newfeature])
                            log.debug(result)

                    # Get Sit Rep Dashboard item (to update "last updated" time text)
                    dashboard_item = gis.content.get(SitRepDashboard_ItemID)
                    dashboard_item_data = dashboard_item.get_data()

                    # Find update text widget
                    for row in dashboard_item_data["widgets"]:
                        if row["name"] == "Update Text":
                            updatetext_index = dashboard_item_data["widgets"].index(row)

                    # Get current time and update widget text to "Last Update:" and datetime 
                    today = datetime.now()
                    dashboard_item_data["widgets"][updatetext_index]["text"] = '<div style="align-items:center; display:flex; justify-content:center; margin-bottom:auto; margin-left:auto; margin-right:auto; margin-top:auto"><h3 style="font-size:14px; text-align:center"><strong>Data Last Updated: ' + today.strftime("%B %#d, %Y, %H:%M hrs") + '</strong></h3></div>'
                    result = dashboard_item.update(data=dashboard_item_data)
                    log.debug(result)
                    success = True

                # If attempt fails, retry attempt (up to 5 times then exit script if unsuccessful)
                except:
                    log.warning(f"Re-Attempting AGO Update. Attempt Number {attempts}")
                    attempts += 1
                    if attempts == 5:
                        log.critical(f"***No More Attempts Left. AGO Update Failed***")
                        break
        else:
            log.critical(f"***Website JSON Data Not Found***")
    else:
        log.critical(f"***Request Module Connection to Website Failed***")

Update_Weather_Alerts()