###========================================================================================================================================================
###     BC Hydro Outages
###     (BCHydro_Outages.py)
###
###     Written by: Paulina Marczak (paulina.marczak@gov.bc.ca) and Michael Dykes (michael.dykes@gov.bc.ca)
###
###     Created: May 27 2021
###     Edited: November 10 2022 (MDykes)
###
###     Purpose: Grab BC Hydro Web Content (from https://www.bchydro.com/power-outages/app/outage-map.html) and update ArcGIS Online Hosted Feature Layer
###==========================================================================================================================================================
# Import libraries/modules
import requests, json, logging
from arcgis.gis import GIS
from arcgis import geometry, features
from datetime import datetime, timezone
    
# Create logger and set logging level (NOTSET,DEBUG,INFO,WARNING,ERROR,CRITICAL)
logging.basicConfig(level=logging.INFO)
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
HydroOutages_ItemID = CONF["HydroOutages_ItemID"]
HydroOutagesLFN_ItemID = CONF["HydroOutagesLFN_ItemID"]

# Request data from bchydro.com outages map and use request module to connect to website data
url = r"https://www.bchydro.com/power-outages/app/outages-map-data.json"
x = requests.get(url)

# Connect to GIS portal
gis = GIS(PORTAL_URL, username=PORTAL_USERNAME, password=PORTAL_PASSWORD, expiration=99999)
# Get Hosted Feature Layers to Update
HFS_item = gis.content.get(HydroOutages_ItemID)
HFS2_item = gis.content.get(HydroOutagesLFN_ItemID)
# Delete all existing feature layer features and reset OBJECTID/FID counter
HFS_item.layers[0].delete_features(where="objectid > 0")
#HFS_item.layers[0].manager.truncate()
HFS2_item.layers[0].delete_features(where="objectid > 0")
#HFS2_item.layers[0].manager.truncate()

# If good web return/connection
if x.status_code == 200:
    # If data that can be read in json is returned
    if x and x.json():
        # Attempt to connect to AGO and update the hosted feature layer
        attempts = 0
        success = False
        # 5 attempts to connect and update the layer 
        while attempts < 5 and not success:
            try:
                # Iterate through bchydro JSON items (each outage is its own item)
                for row in x.json():
                    # Build LAT/LONG list pairings from unseparated list of LAT/LONGS from website JSON
                    latlong_list = [list(a) for a in zip(row["polygon"][::2],row["polygon"][1::2])]
                    # Create Polygon Geometry WKID:4326 = WGS 1984
                    geom = geometry.Geometry({"type": "Polygon", "rings" : [latlong_list],"spatialReference" : {"wkid" : 4326}})
                    # Build attributes to populate feature attribute table, check for none values in the EST_TIME_ON, OFFTIME and UPDATED date fields
                    attributes = {"OUTAGE_ID":row['id'], 
                            "GIS_ID":row['gisId'],
                            "REGION_ID": row['regionId'],
                            "REGION": row['regionName'],
                            "MUNI": row['municipality'],
                            "DETAILS": row['area'],
                            "CAUSE": row['cause'],
                            "AFFECTED":  row['numCustomersOut'],
                            "CREW_STATUS": row['crewStatusDescription'],
                            "EST_TIME_ON": datetime.utcfromtimestamp(row['dateOn']/1000).replace(tzinfo=timezone.utc).astimezone(tz=None) if row['dateOn'] else None,
                            "OFFTIME": datetime.utcfromtimestamp(row['dateOff']/1000).replace(tzinfo=timezone.utc).astimezone(tz=None) if row['dateOff'] else None,
                            "UPDATED": datetime.utcfromtimestamp(row['lastUpdated']/1000).replace(tzinfo=timezone.utc).astimezone(tz=None) if row['lastUpdated'] else None,
                            "CREW_ETA": datetime.utcfromtimestamp(row['crewEta']/1000).replace(tzinfo=timezone.utc).astimezone(tz=None) if row['crewEta'] else None,
                            "CREW_ETR": datetime.utcfromtimestamp(row['crewEtr']/1000).replace(tzinfo=timezone.utc).astimezone(tz=None) if row['crewEtr'] else None,
                            "SHOW_ETA": row['showEta'],
                            "SHOW_ETR": row['showEtr']}
                    # Create new feature
                    newfeature = features.Feature(geom,attributes)
                    # Add feature to existing hosted feature layer
                    result = HFS_item.layers[0].edit_features(adds = [newfeature])
                    result2 = HFS2_item.layers[0].edit_features(adds = [newfeature])
                    success = True

            # If attempt fails, retry attempt (up to 5 times then exit script if unsuccessful)
            except:
                log.exception("message")
                log.warning(f"Re-Attempting AGO Update. Attempt Number {attempts}")
                attempts += 1
                if attempts == 5:
                    log.critical(f"***No More Attempts Left. AGO Update Failed***")
                    sys.exit(1)
    else:
        log.critical(f"***Website JSON Data Not Found***")
else:
    log.critical(f"***Request Module Connection to Website Failed***")