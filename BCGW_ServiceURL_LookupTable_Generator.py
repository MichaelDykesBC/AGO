# Import required libraries/modules
import requests, csv, getpass
from arcgis.gis import GIS
from difflib import SequenceMatcher

#Username and Password Variables from User Entry (getpass doesn't echo, and displays encrypted for security)
PORTAL_URL = "https://bcgov03.maps.arcgis.com"
PORTAL_USERNAME = os.getenv('GEOHUB_USERNAME')
PORTAL_PASSWORD = os.environ.get('GEOHUB_PASSWORD')

#ArcGIS Online Connection (url,username,password)
gis = GIS(PORTAL_URL, username=PORTAL_USERNAME, password=PORTAL_PASSWORD, expiration=9999)

AGO_AUTH_Dict = {}
AGO_DEP_Dict = {}
for item in gis.content.search(query="owner: Province.Of.British.Columbia",item_type="Feature Service", max_items=5000):
    if item.content_status != "deprecated":
        if item.title.lower() in AGO_AUTH_Dict:
            AGO_AUTH_Dict[item.title.lower()].append(item)
        else:
            AGO_AUTH_Dict[item.title.lower()] = [item]
    else:
        if item.title.lower() in AGO_DEP_Dict:
            AGO_DEP_Dict[item.title.lower()].append(item)
        else:
            AGO_DEP_Dict[item.title.lower()] = [item]
        
for item in gis.content.search(query="owner: Province.Of.British.Columbia",item_type="Map Service", max_items=5000):
    if item.content_status == "deprecated":
        if item.title.lower() in AGO_DEP_Dict:
            AGO_DEP_Dict[item.title.lower()].append(item)
        else:
            AGO_DEP_Dict[item.title.lower()] = [item]

Resturl = r'https://maps.gov.bc.ca/arcgis/rest/services/mpcm/bcgwpub/MapServer/'
response = requests.get(Resturl + '?f=json')
sitejson = response.json()

MPCM_Dict = {}
for layer in sitejson['layers']:
    MPCM_Dict[layer['name'].lower()] = {"URL":Resturl + str(layer['id'])}

for k,v in MPCM_Dict.items():
    if k.lower() in AGO_AUTH_Dict:
        if len(AGO_AUTH_Dict[k]) == 1:
            if "AUTH" in v:
                MPCM_Dict[k.lower()]["AUTH"].append(AGO_AUTH_Dict[k][0])
            else:
                MPCM_Dict[k.lower()]["AUTH"] = [AGO_AUTH_Dict[k][0]]
        else:
            for row in AGO_AUTH_Dict[k]:
                if "AUTH" in v:
                    MPCM_Dict[k.lower()]["AUTH"].append(row)
                else:
                    MPCM_Dict[k.lower()]["AUTH"] = [row]
    else:
        Auth_List = []
        for k2,v2 in AGO_AUTH_Dict.items():
            for row in v2:
                Str_Similarity = SequenceMatcher(a=k.lower(),b=k2.lower()).ratio()
                if k.lower() in k2.lower() or k2.lower() in k.lower():
                    Auth_List.append((Str_Similarity,k2,row))
                elif Str_Similarity >= 0.8:
                    Auth_List.append((Str_Similarity,k2,row))
        if Auth_List:
            if len(Auth_List) == 1:
                if "AUTH" in v:
                    MPCM_Dict[k]["AUTH"].append(Auth_List[0][2])
                else:
                    MPCM_Dict[k]["AUTH"] = [Auth_List[0][2]]
            else:
                if "AUTH" in v:
                    MPCM_Dict[k]["AUTH"].append(sorted(Auth_List,key=lambda x : x[0],reverse=True)[0][2])
                else:
                    MPCM_Dict[k]["AUTH"] = [sorted(Auth_List,key=lambda x : x[0],reverse=True)[0][2]]

for k,v in MPCM_Dict.items():
    if k.lower() in AGO_DEP_Dict:
        if len(AGO_DEP_Dict[k]) == 1:
            if "DEP" in v:
                MPCM_Dict[k.lower()]["DEP"].append(AGO_DEP_Dict[k][0])
            else:
                MPCM_Dict[k.lower()]["DEP"] = [AGO_DEP_Dict[k][0]]
        else:
            for row in AGO_DEP_Dict[k]:
                if "DEP" in v:
                    MPCM_Dict[k.lower()]["DEP"].append(row)
                else:
                    MPCM_Dict[k.lower()]["DEP"] = [row]
    else:
        Dep_List = []
        for k2,v2 in AGO_DEP_Dict.items():
            for row in v2:
                Str_Similarity = SequenceMatcher(a=k.lower(),b=k2.lower()).ratio()
                if k.lower() in k2.lower() or k2.lower() in k.lower():
                    Dep_List.append((Str_Similarity,k2,row))
                elif Str_Similarity >= 0.8:
                    Dep_List.append((Str_Similarity,k2,row))
        if Dep_List:
            if len(Dep_List) == 1:
                if "DEP" in v:
                    MPCM_Dict[k]["DEP"].append(Dep_List[0][2])
                else:
                    MPCM_Dict[k]["DEP"] = [Dep_List[0][2]]
            else:
                if "DEP" in v:
                    MPCM_Dict[k]["DEP"].append(sorted(Dep_List,key=lambda x : x[0],reverse=True)[0][2])
                else:
                    MPCM_Dict[k]["DEP"] = [sorted(Dep_List,key=lambda x : x[0],reverse=True)[0][2]]

with open(r'C:\Users\Mike\Desktop\AGO_BCGW_Lookup.csv', 'w', newline='') as csvfile: 
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(["OLD_SERVICE_TITLE","OLD_SERVICE_URL","AUTHORITATIVE_AGO_TITLE","AUTHORITATIVE_AGO_SERVICE_URL","AUTHORITATIVE_AGO_ITEMID","ASSOCIATED_DEPRECATED_ITEMIDS","ASSOCIATED_DEPRECATED_URLS"])               
    for k,v in MPCM_Dict.items():
        field1 = k
        field2 = v["URL"]
        field3 = None
        field4 = None
        field5 = None
        field6 = None
        field7 = None
        if "AUTH" in v:
            field3 = v["AUTH"][0].title
            field4 = v["AUTH"][0].url
            field5 = v["AUTH"][0].id
        if "DEP" in v:
            for row in v["DEP"]:
                if field6:
                    field6 = field6 + "," + row.id
                else:
                    field6 = row.id
                if field7:
                    field7 = field7 + "," + row.url
                else:
                    field7 = row.url
        csvwriter.writerow([field1,field2,field3,field4,field5,field6,field7])