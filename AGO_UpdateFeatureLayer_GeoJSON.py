###================================================================================================================================================
### AGO_UpdateFeatureLayer_GeoJSON.py
###     Written by: Michael Dykes
###     Created: 2019-08-19
###     Edited: 2019-08-30 (MDykes)
###
###     Purpose: Update Existing Content in ArcGIS Online from Feature Class (Through GeoJSON) - Tested with Same Fields Just More or Less Features
###================================================================================================================================================
from arcgis.gis import GIS
import arcpy, os, getpass

# New Feature Class (fields should match content overwriting)
Featureclass = r'S:\Gis\Requests\Mapping\MIRR\Treaty_8_TLE_TLA\Geodatabase\Treaty8.gdb\Halfway_TLE'

# Set Workspace (feel free to use my "Python_Host" work area for scratch work)
arcpy.env.workspace = r"S:\Gis\Python\AGO\Python_Host\Python_Host.gdb"
arcpy.env.overwriteOutput = True

# Create GeoJson file from Feature Layer (requires Feature Layer and not Feature Class input)
# (**Even if Title Property is Different, AGO Doesn't Accept Duplicate FileNames & Extensions i.e You Can Only Have One 'AGOJsonFile.geojson' Layer File in AGO Even if the Titles are Different**)
jsonfilepath = r"S:\Gis\Python\AGO\Python_Host\Halfway_TLE.geojson"
featurelayer = arcpy.MakeFeatureLayer_management(Featureclass,"in_memory/featurelayer")
geojsonfile = arcpy.FeaturesToJSON_conversion(featurelayer,jsonfilepath,geoJSON="GEOJSON")

# User Entry for AGO username, password, and Hosted Feature Layer Title to Update (echo-free so your password won't be shown in terminal or output)
username = input("Username :")
password = getpass.getpass(prompt='Password: ')

# Create Connection to AGO (change portal string if necessary i.e. for EMGeoHub)
gis = GIS('https://governmentofbc.maps.arcgis.com/',username,password)

# Search for content owned by username and titled with Hosted Feature Layer Title (change item type if working with something other than a feature layer)
item_search = gis.content.search(query="owner: MDYKES.BC AND title: Halfway_TLE", item_type="Feature Layer")
print(item_search)

# Content Search Not Reliable (Grabs Content with Aproximate Match to Title as Well) so Do Some More Python to Make Sure the Item is the One You Want
item = None
if item_search:
   if len(item_search) == 1:
      item = item_search[0] 
   else:
      for row in item_search:
         if row['title'] == "Halfway_TLE":
            item = row

if item:
    print(item, item.id)
    
    # Set AGO Item Properties and Add Content (Can add 'folder=*foldername*' Parameter to Add Content Directly to Existing AGO Folder)
    fc_toadd_properties = {'title': 'Halfway_TLE','tags': 'AGRI', 'type': 'GeoJson'}
    fc_item = gis.content.add(item_properties=fc_toadd_properties, data=jsonfilepath)

    fc_item.publish(overwrite=True)

else:
    print("No AGO Item Found")

# Delete GeoJson File from Scratch Workplace
os.remove(jsonfilepath)

print("Done")