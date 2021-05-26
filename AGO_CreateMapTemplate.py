###===========================================================================================================
### AGO_CreateMapTemplate.py
###     Written by: Michael Dykes
###     Created: 2019-08-07
###     Edited: 2019-08-30 (MDykes)
###
###     Purpose: Create New Web Map Using Template JSON Files to Set BCGW Content Symbology, Popups, etc
###============================================================================================================
from arcgis.gis import GIS
from arcgis.mapping import WebMap
import json, arcpy, getpass

# List of Existing Scraped JSON Content From Template
ALR_JSON_File = r'S:\Gis\Python\AGO\Map Base JSON\ALR_JSON.txt'
AgCAP_JSON_File = r'S:\Gis\Python\AGO\Map Base JSON\AgCapability_JSON.txt'
PMBC_JSON_File = r'S:\Gis\Python\AGO\Map Base JSON\PMBC_JSON.txt'
CrownTenureAll_File = r'S:\Gis\Python\AGO\Map Base JSON\CrownTenureAll_JSON.txt'
CrownTenureAquaculture_File = r'S:\Gis\Python\AGO\Map Base JSON\CrownTenureAquaculture_JSON.txt'
RangeTenure_JSON_File = r'S:\Gis\Python\AGO\Map Base JSON\RangeTenure_JSON.txt'
RangePasture_JSON_File = r'S:\Gis\Python\AGO\Map Base JSON\RangePasture_JSON.txt'
SoilSurvey_JSON_File = r'S:\Gis\Python\AGO\Map Base JSON\SoilSurvey_JSON.txt'
LivestockLarge_JSON_File = r'S:\Gis\Python\AGO\Map Base JSON\LivestockLarge_JSON.txt'
IndianReserves_JSON_File = r'S:\Gis\Python\AGO\Map Base JSON\IndianReserves_JSON.txt'
Greenspace_JSON_File = r'S:\Gis\Python\AGO\Map Base JSON\Greenspace_JSON.txt'
BCParks_JSON_File = r'S:\Gis\Python\AGO\Map Base JSON\BCParks_JSON.txt'
NationalParks_JSON_File = r'S:\Gis\Python\AGO\Map Base JSON\NationalParks_JSON.txt'

username = input("Username :")
password = getpass.getpass(prompt='Password: ')

gis = GIS('https://governmentofbc.maps.arcgis.com/',username,password)

# Initialize New Web Map Content
wm = WebMap()

# Get Existing AGO Content (BCGW) Using Item ID
ALR = gis.content.get('0ce279465c97462e8b583e6d67987bdd')
AgCAP = gis.content.get('3fb6d970b6204c3aaee400c7a73d68e7')
PMBC = gis.content.get('ce7fd87476b54100a3b158c9dae7e9b7')
CrownTenures = gis.content.get('a009af6874154d53bafa540c29c5faf8')
RangeTenure = gis.content.get('439b18bcd65b4fb0bf943876960b172a')
RangePasture = gis.content.get('743270b1b89c45b49efb5d4241baf97a')
SoilSurvey = gis.content.get('ee6879ca62194b88aee3a18f954a70f3')
LivestockLarge = gis.content.get('1649d11f18f443ecae7003afa2df99b3')
IndianReserve = gis.content.get('6f1e8fc7bd24460cad0ae533eb4acfe2')
Greenspace = gis.content.get('7523d1849d6e46f5b997d833e849d88b')
BCParks = gis.content.get('8d1d458346bd42adbedbd9754dac0b33')
NationalParks = gis.content.get('5ade04eb4d7145eab978ba0cff1e6ba8')

# List of Items to Add - Order Matters (First item will be at the bottom of the table of contents)
Layers_toadd = [NationalParks,BCParks,Greenspace,IndianReserve,LivestockLarge,SoilSurvey,RangePasture,RangeTenure,CrownTenures,PMBC,AgCAP,ALR]

# Iterate Trhough and Add Items to Map
for layer in Layers_toadd:
    wm.add_layer(layer)
    
# Dictionary of Items : Original Title, JSON File Path, New Title (if desired), Visibility True/False
LayerDict = {'ALC ALR Polygons':[ALR_JSON_File,'Agricultural Land Reserve',True],
'Ag_Capability':[AgCAP_JSON_File,"Agricultural Capability",False],
'ParcelMap BC Parcel Fabric':[PMBC_JSON_File,None,False],
'TANTALIS - Crown Tenures':[CrownTenureAll_File,'Crown Tenures (All)',False],
'Range Tenure':[RangeTenure_JSON_File,None,False],
'Range Pastures':[RangePasture_JSON_File,None,False],
'Soil Survey Spatial View':[SoilSurvey_JSON_File,'Soil Survey',False],
'Livestock at Large Regulations in British Columbia':[LivestockLarge_JSON_File,'Livestock at Large Regulations',False],
'Indian Reserves & Band Names - Administrative Boundaries':[IndianReserves_JSON_File,'Indian Reserves',False],
'Local and Regional Greenspaces':[Greenspace_JSON_File,None,False],
'BC Parks, Ecological Reserves, and Protected Areas':[BCParks_JSON_File,None,False],
'National Parks of Canada within British Columbia':[NationalParks_JSON_File,None,False]}

LayerDict2 = {'TANTALIS - Crown Tenures':[CrownTenureAquaculture_File,'Crown Tenures - Aquaculture',False]}

# Grab Map Item Operational Layers, Match to Items in Dictionary Above by Title
for layer in wm.definition['operationalLayers']:
    if layer['title'] in LayerDict:
        # Keep Original Title for Updating Content if Changing Title (Key Will Change)
        orig_title = layer['title']

        # Get List Index of Item (Updating Content Based on Index in OperationalLayers List in AGO)
        index = wm.definition['operationalLayers'].index(layer)

        # Change Dictionary/JSON values (Visiblity/Title Below) **Not Working Right Now***
        if LayerDict[layer['title']][2] is False:
            layer['visibility'] = False
        else:
            layer['visibility'] = True

        if LayerDict[layer['title']][1]:
            layer['title'] = LayerDict[layer['title']][1]

        # Grab JSON File Content and Use to Update AGO JSON (Using Layer Index in Operational Layers List)
        with open(LayerDict[orig_title][0]) as json_file:
            data = json.load(json_file)
            wm.definition['operationalLayers'][index] = data
            

# Set New Item Properties and Save Map
web_map_properties = {'title':'AGRI Base Template','snippet':'Base Template for BC Ministry of Agriculture Web Maps','tags':'AGRI'}
web_map_item = wm.save(item_properties=web_map_properties)

print("Done")