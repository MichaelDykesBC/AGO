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
from arcgis.features import FeatureLayerCollection, FeatureLayer
import json, arcpy, getpass

username = input("Username :")
password = getpass.getpass(prompt='Password: ')

gis = GIS('https://governmentofbc.maps.arcgis.com/',username,password)

# Search for content owned by username and titled with Hosted Feature Layer Title (change item type if working with something other than a feature layer)
item_search = gis.content.search(query="owner: MDYKES.BC AND title: Kitselas2017", item_type="Feature Layer Collection")

print(item_search)

# Content Search Not Reliable (Grabs Content with Aproximate Match to Title as Well) so Do Some More Python to Make Sure the Item is the One You Want
if item_search:
   if len(item_search) == 1:
      item = item_search[0] 
   else:
      for row in item_search:
         if row['title'] == "Kitselas2017":
            item = row

if item:
   itemlayer1 = item.layers[0]
   itemlayer1.properties['editingInfo']['lastEditDate'] = " "
   for row in itemlayer1.properties['fields']:
      if row['name'] == 'SITE_SUIT':
         newvalue = {'name': 'Very High', 'code': 'Very High'}
         row['domain']['codedValues'].append(newvalue)

   print(itemlayer1.properties['editingInfo'])

   update_result = itemlayer1.manager.update_definition(itemlayer1.properties)

print("Done")