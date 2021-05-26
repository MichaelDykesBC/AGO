from arcgis.gis import GIS
from arcgis.features import FeatureLayerCollection
import arcpy, os, getpass, json

Featureclass = r'S:\Gis\Requests\Mapping\MIRR\Treaty_8_TLE_TLA\Geodatabase\backups\Treaty8_July2019.gdb\Doig_TLE_20180914'

SDDraftfilepath = r"S:\Gis\Python\AGO\Python_Host\PythonSD.sddraft"
SDfilepath = r"S:\Gis\Python\AGO\Python_Host\PythonSD.sd"

aprx = arcpy.mp.ArcGISProject(r"S:\Gis\Python\AGO\Python_Host\Python_Host.aprx")
map = aprx.listMaps()[0]
map.addDataFromPath(Featureclass)
aprx.save()

print(map.listLayers()[0])
lyrs=[]
lyrs.append(map.listLayers()[0])

arcpy.mp.CreateWebLayerSDDraft(lyrs,SDDraftfilepath,"PythonTest1",overwrite_existing_service=True)
arcpy.StageService_server(SDDraftfilepath, SDfilepath)

layerlist = map.listLayers()
for layer in layerlist:
    map.removeLayer(layer)
aprx.save()

username = input("Username :")
password = getpass.getpass(prompt='Password: ')

gis = GIS('https://governmentofbc.maps.arcgis.com/',username,password)

item = gis.content.search(query="owner:MDYKES.BC AND title:PythonTest1", item_type="Service Definition")[0]
print(item, item.id)

item.update(data=SDfilepath)
item.publish(overwrite=True)

os.remove(SDDraftfilepath)
os.remove(SDfilepath)

print("Done")
