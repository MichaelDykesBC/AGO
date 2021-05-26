###=========================================================================================================
### AGO_ItemToJSONFile.py
###     Written by: Michael Dykes
###     Created: 2019-08-07
###     Edited: 2019-08-30 (MDykes)
###
###     Purpose: Scrape AGO Map Content (layer symbology, popups, etc) to Text File For Use In Template
###=========================================================================================================
from arcgis.gis import GIS
from arcgis.mapping import WebMap
import json, arcpy, getpass

username = input("Username :")
password = getpass.getpass(prompt='Password: ')
Host_FL = input("Hosted Feature Layer Title:")

gis = GIS('https://governmentofbc.maps.arcgis.com/',username,password)

# Search for content owned by username and titled with Hosted Feature Layer Title (change item type if working with something other than a feature layer)
item_search = gis.content.search(query="owner:" + username + " AND title:" + Host_FL, item_type="Web Map")

# Content Search Not Reliable (Grabs Content with Aproximate Match to Title as Well) so Do Some More Python to Make Sure the Item is the One You Want
if item_search:
   if len(item_search) == 1:
      item = item_search[0] 
   else:
      for row in item_search:
         if row['title'] == "Web Map Template":
            item = row

if item:
   JSON_File = r'S:\Gis\Python\AGO\Map Base JSON\ALR_JSON.txt'

   # Grab Item Data From AGO (JSON)
   item_data = item.get_data()

   # Check Map Layers, Isolate Layer Setup JSON (Symbology, Pop-ups, etc), Create Text File and Dump/Write JSON into it
   for row in item_data['operationalLayers']:
      if row['title'] == 'Agricultural Land Reserve':
         with open(ALR_JSON_File, 'w') as outfile:
            json.dump(row, outfile)

print("Done")