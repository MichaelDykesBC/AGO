from arcgis.gis import GIS, ContentManager
import json, arcpy, getpass

WebApp_JSON_File = r'S:\Gis\Python\AGO\Map Base JSON\WebApp_JSON.txt'

username = input("Username :")
password = getpass.getpass(prompt='Password: ')

gis = GIS('https://governmentofbc.maps.arcgis.com/',username,password)

item_search = gis.content.search(query="owner:MDYKES.BC AND title:Land Analysis Web App Template", item_type="Web Mapping Application")

if item_search:
   if len(item_search) == 1:
      item = item_search[0] 
   else:
      for row in item_search:
         if row['title'] == "Web Map Template":
            item = row

newitem = gis.content.clone_items([item], folder=None, item_extent=None, use_org_basemap=False, copy_data=True, search_existing_items=True, item_mapping=None, group_mapping=None, owner=None)

print(newitem)

'''
web_app_properties = {'title':'Land Analysis Web App','data':WebApp_JSON_File,'tags':'AGRI','type':"Web Mapping Application"}
item = gis.content.add(item_properties=web_app_properties)

print(item, item.id, item.url)

# for layer in wm.definition['operationalLayers']:
#     if layer['title'] in LayerDict:
#         orig_title = layer['title']
#         index = wm.definition['operationalLayers'].index(layer)
#         # if LayerDict[layer['title']][2] is False:
#         #     layer['visibility'] = False
#         # else:
#         #     print(layer['title'])
#         #     layer['visibility'] = True
#         # if LayerDict[layer['title']][1]:
#         #     layer['title'] = LayerDict[layer['title']][1]
#         with open(LayerDict[orig_title][0]) as json_file:
#             data = json.load(json_file)
#             wm.definition['operationalLayers'][index] = data

# web_map_properties = {'title':'AGRI Base Template','snippet':'Base Template for BC Ministry of Agriculture Web Maps','tags':'AGRI'}
# web_map_item = wm.save(item_properties=web_map_properties)
'''

print("Done")