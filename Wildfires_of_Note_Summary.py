import sys, pandas, json, pytz, datetime
import collections
from arcgis.gis import GIS
from arcgis import geometry, features

# Load config file to get AGO parameter values
config_file = sys.argv[1]
with open(config_file) as json_conf : 
    CONF = json.load(json_conf)

# BC GeoHub parameters and credentials needed for connection
PORTAL_URL = CONF["AGO_Portal_URL"]
PORTAL_USERNAME = sys.argv[2]
PORTAL_PASSWORD = sys.argv[3]

# Get ItemIDs from config file
FireCentre_ItemID = CONF["FireCentre_ItemID"]
FireLocation_ItemID = CONF["FireLocation_ItemID"]
WildfireTable_ItemID = CONF["WildfireTable_ItemID"]
SitRepDashboard_Mobile_ItemID = CONF["SitRepDashboard_Mobile_ItemID"]
SitRepDashboard_Desktop_ItemID = CONF["SitRepDashboard_Desktop_ItemID"]

# Build AGO Connection
gis = GIS(PORTAL_URL,PORTAL_USERNAME,PORTAL_PASSWORD, expiration=9999) 

# Grab Fire Centre HFL and create spatial dataframe
FireCentre_item = gis.content.get(FireCentre_ItemID)
FireCentre_layer = FireCentre_item.layers[0]
FireCentre_fset = FireCentre_layer.query()
FireCentre_df = FireCentre_fset.sdf

# Grab Fire Location HFL and create spatial dataframe
Fire_item = gis.content.get(FireLocation_ItemID)
Fire_layer = Fire_item.layers[0]
Fire_fset = Fire_layer.query()
Fire_df = Fire_fset.sdf

# Get existing wildfire of note summary table in AGO for updating
WildfireTable_item = gis.content.get(WildfireTable_ItemID)
WildfireTable_layer = WildfireTable_item.layers[0]

# Wipe existing wildfire of note data from table
WildfireTable_layer.delete_features(where="objectid > 0")
#WildfireTable_layer.manager.truncate()

# Create dictionary with fire centres names as keys and empty lists as values (to be populated with fires of note)
fire_by_centre_dict = {f: [] for f in FireCentre_df['MOF_FIRE_CENTRE_NAME'].unique()}

# Iterate through fires of note from Fire Location HFL and add this data to dictionary created above
for index, row in Fire_df.iterrows():
    if row["PublicStatus"] == "Fire of Note":
        toappend = row["GEOGRAPHIC_DESCRIPTION"],row["INCIDENT_NUMBER_LABEL"],row["FIRE_SIZE_HA"],row["STAGE_OF_CONTROL_DESC"],row["WFNURL"]
        fire_by_centre_dict[row["FIRE_CTR_ORG_UNIT_NAME"]].append(toappend)

# Iterate through existing the fire centre HFL to get the geometry/polygons
for index, row in FireCentre_df.iterrows():
    geom = geometry.Geometry(row["SHAPE"])
    # Build attributes to populate feature attribute table, create  a sum of the fires of note based on their stage of control
    attributes = {"MOF_FIRE_CENTRE_ID":row['MOF_FIRE_CENTRE_ID'],
                 "MOF_FIRE_CENTRE_NAME":row['MOF_FIRE_CENTRE_NAME'],
                 "OutOfControl":sum(1 for elem in fire_by_centre_dict[row['MOF_FIRE_CENTRE_NAME']] if elem[3] == "Out Of Control"),
                 "BeingHeld":sum(1 for elem in fire_by_centre_dict[row['MOF_FIRE_CENTRE_NAME']] if elem[3] == "Being Held"),
                 "UnderControl":sum(1 for elem in fire_by_centre_dict[row['MOF_FIRE_CENTRE_NAME']] if elem[3] == "Under Control"),
                 "Total":sum(1 for elem in fire_by_centre_dict[row['MOF_FIRE_CENTRE_NAME']] if elem[3] != "Out")}
    # Create new feature
    newfeature = features.Feature(geom,attributes)
    # Add feature to existing hosted feature layer
    result = WildfireTable_layer.edit_features(adds = [newfeature])

firecentre_list = []
for firecentre,firelist in fire_by_centre_dict.items():
    toappend = firecentre,len(firelist)
    firecentre_list.append(toappend)

firecentre_sorted_list = sorted(sorted(firecentre_list, key=lambda x: x[0]),key=lambda x: x[1],reverse=True)

# Build HTML table to update in Wildfire of Note dashboard in the Situation Report Application
dashboard_text = ""
for firecentre in firecentre_sorted_list:
    header = '<p><span style="font-size:11pt"><strong>' + firecentre[0] + '</strong></span></p>'
    if fire_by_centre_dict[firecentre[0]]:
        header = header + "<ul>"
        for fire in fire_by_centre_dict[firecentre[0]]:
            header = header + f'<li><a href="{str(fire[4])}" style="color: #99ccff; font-weight: bold;">{str(fire[0])}</a> ({str(fire[1])}), {str(fire[2])} hectares, {str(fire[3])}</li>'
        header = header + '</ul>'
    else:
        header = header + "<ul><li>None</li></ul>"
    dashboard_text = dashboard_text + header

# Get Situation Report Application items from AGO
dashboard_item_mobile = gis.content.get(SitRepDashboard_Mobile_ItemID)
dashboard_item_desktop = gis.content.get(SitRepDashboard_Desktop_ItemID)

dashboard_toupdate = [dashboard_item_mobile,dashboard_item_desktop]

# Update Sit Rep Dashboards with new HTML tables
for dashboard in dashboard_toupdate:
    dashboard_item_data = dashboard.get_data()

    for row in dashboard_item_data["widgets"]:
        if row["name"] == "Fires of Note Text":
            firetext_index = dashboard_item_data["widgets"].index(row)
            dashboard_item_data["widgets"][firetext_index]["text"] = dashboard_text
        if row["name"] == "Update Text":
            updatetext_index = dashboard_item_data["widgets"].index(row)
            today = datetime.datetime.now()
            dashboard_item_data["widgets"][updatetext_index]["text"] = '<div style="align-items:center; display:flex; justify-content:center; margin-bottom:auto; margin-left:auto; margin-right:auto; margin-top:auto"><h3 style="font-size:14px; text-align:center"><strong>Data Last Updated: ' + today.strftime("%B %#d, %Y, %H:%M hrs") + '</strong></h3></div>'

    dashboard.update(data=dashboard_item_data)