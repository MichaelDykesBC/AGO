from arcgis.gis import GIS
from arcgis.features import FeatureLayerCollection
import arcpy, getpass
# Saulteau_TLA, Saulteau_TLE
#UpdateItemName = "Saulteau_TLE"
#UpdateFields =  ["SITE_SUIT","SITE_SUIT_COMMENT","AG_VALUE","AG_VALUE_COMMENT","AG_CAP_RATING","AG_CAP_COMMENT","ANALYZED_BY","ANALYSIS_DATE","RECOMMENDATION"]

#gdb = r'S:\Gis\Requests\Mapping\MIRR\Treaty_8_TLE_TLA\Geodatabase\Treaty8.gdb'

username = input("Username :")
password = getpass.getpass(prompt='Password: ')

gis = GIS('https://governmentofbc.maps.arcgis.com/',username,password)

# Search items by username
items = gis.content.search(query="owner:" + username, item_type="Feature Service", max_items=1000)

# Loop through each item and if equal to Feature service then download it
for item in items:
   print(item.title,item.type)
   if item.type == 'Feature Service':
      result = item.export(item.title, "File Geodatabase")
      result.download(r'S:\Gis\User_workspaces\MDykes\AGO_Backup')
      # Delete the item after it downloads to save space (OPTIONAL)
      result.delete()

'''
ItemToScrape = None
if item_search:
   for item in item_search:
      if UpdateItemName == item.title:
         ItemToScrape = item

if ItemToScrape:
   print("Scraping")
   LayerToScrape = ItemToScrape.layers[0]
   fset = LayerToScrape.query()
   features = fset.features
   UpdateDict = {}
   for feat in features:
      UpdateDict[feat.attributes['AGRI_ID']] = [feat.attributes[r] for r in UpdateFields]
   with arcpy.da.UpdateCursor(gdb + "/" + UpdateItemName,["AGRI_ID","SITE_SUIT","SITE_SUIT_COMMENT","AG_VALUE","AG_VALUE_COMMENT","AG_CAP_RATING","AG_CAP_COMMENT","ANALYZED_BY","ANALYSIS_DATE","RECOMMENDATION"]) as cursor:
      for row in cursor:
         if str(row[0]) in UpdateDict:
            row[1] = UpdateDict[str(row[0])][0]
            row[2] = UpdateDict[str(row[0])][1]
            row[3] = UpdateDict[str(row[0])][2]
            row[4] = UpdateDict[str(row[0])][3]
            row[5] = UpdateDict[str(row[0])][4]
            row[6] = UpdateDict[str(row[0])][5]
            row[7] = UpdateDict[str(row[0])][6]
            row[8] = UpdateDict[str(row[0])][7]
            row[9] = UpdateDict[str(row[0])][8]
            cursor.updateRow(row)

print("Done")
'''