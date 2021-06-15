###=============================================================================================================================================
###     AGO_BCGW_Updater.py
###     Written by: Michael Dykes
###     Created: 2021-06-14
###     Edited: 2021-06-15 (MDykes)
###
###     Purpose: Update BCGW ArcGIS Online JSON Content via Lookup Table (AGO_BCGW_Lookup.csv)
###=============================================================================================================================================
# Import required libraries/modules
import os, getpass, csv, json
from arcgis.gis import GIS
from functools import reduce
from operator import getitem

# Set path for backup JSON text files to wherever this script is sitting
BackupPath = os.path.dirname(os.path.realpath(__file__))

# Username and Password Variables from User Entry (getpass doesn't echo, and displays encrypted for security)
username = input("Username :")
password = getpass.getpass(prompt='Password: ')

# ArcGIS Online Connection (url,username,password)
gis = GIS('https://governmentofbc.maps.arcgis.com/',username,password)

# Function to update values in nested dictionaries using a list of keys that lead to the value
def set_nested_item(dataDict, mapList, val):
    reduce(getitem, mapList[:-1], dataDict)[mapList[-1]] = val
    return dataDict

# Function to search through a nested dictionary (including lists) to find a certain key, and then append the key path and value to a "storage" list
def JSONsearch(storage, haystack, needle, path=None):
    storage = storage
    if path is None:
        path = []
    if isinstance(haystack, dict):
        if needle in haystack:
            path.append(needle)
            toappend = path,haystack[needle]
            storage.append(toappend)
        for k, v in haystack.items():
            JSONsearch(storage, v, needle, path + [k])
    elif isinstance(haystack, list):
        for idx, v in enumerate(haystack):
            JSONsearch(storage, v, needle, path + [idx])

# Search through lookup table and build dictionaries for old/deprecated urls and old/deprecated itemids with what they should be updated to (new authoritative items and urls) as values
OldUrl_Dict = {}
OldItemID_Dict = {}
with open(r"C:\Users\Mike\Desktop\AGO_BCGW_Lookup.csv", newline='') as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        OldUrl_Dict[row[1]] = [row[2],row[3],row[5]]
        if "dynamicLayer?layer=" in row[7]:
            if row[7] in OldUrl_Dict:
                if OldUrl_Dict[row[7]][0][1] != row[3]:
                    toappend = row[2],row[3],row[5]
                    OldUrl_Dict[row[7]].append(toappend)
            else:
                OldUrl_Dict[row[7]] = [row[2],row[3],row[5]]
        else:
            for item in row[7].split(","):
                if item:
                    if item in OldUrl_Dict:
                        if OldUrl_Dict[item][1] != row[3]:
                            toappend = row[2],row[3],row[5]
                            OldUrl_Dict[item].append(toappend)
                    else:
                        OldUrl_Dict[item] = [row[2],row[3],row[5]]

        for item in row[6].split(","):
            if item:
                if item in OldItemID_Dict:
                    if OldItemID_Dict[item][1] != row[3]:
                        toappend = row[2],row[3],row[5]
                        OldItemID_Dict[item].append(toappend)
                else:
                    OldItemID_Dict[item] = [row[2],row[3],row[5]]

# Search through your items ("Web Map","Web Mapping Application","Web Experience","StoryMap","Dashboard","Application") get the data JSON, search for itemID, url, and baseURL keys, see if they exist in the deprecated dictionaries then update to the new values
for item in gis.content.search(query="* AND \  owner:" + gis.users.me.username, max_items=1000):
    if item.type in ["Web Map","Web Mapping Application","Web Experience","StoryMap","Dashboard","Application"]:
        StorageList = []
        item_data = item.get_data()
        JSONsearch(StorageList,item_data,"itemId")
        JSONsearch(StorageList,item_data,"url")
        JSONsearch(StorageList,item_data,"baseURL")
        if StorageList:
            with open(BackupPath + "\\" + item.title + "_JSONBackup.txt", 'w') as outfile:
                json.dump(item_data, outfile)
            for row in StorageList:
                if row[1] in OldUrl_Dict:
                    set_nested_item(item_data,row[0],OldUrl_Dict[row[1]][1])
                if row[1] in OldItemID_Dict:
                    set_nested_item(item_data,row[0],OldItemID_Dict[row[1]][2])
            # *** UPDATES YOUR AGO JSON, ONLY CALL THIS FUNCTION IF YOU MEAN IT ***
            item.update(data=item_data)
print("Done")