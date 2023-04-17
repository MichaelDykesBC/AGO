import arcpy

# Input Point Dataset to Remove Duplicates
pointdataset = r'C:\Users\Mike\AppData\Local\Temp\ArcGISProTemp43708\b3f29257-8e7b-4a8f-a055-9f4b65acb362\Default.gdb\TestPoints'

# Empty dictionary to store unique keys (LAT/LONG/LICENSEE) and values (ObjectIDs)
UniqueDict = {}
# Iterate through points features
with arcpy.da.SearchCursor(pointdataset, ["LAT","LONG","LICENSEE","OID@"]) as cursor:
    for row in cursor:
        # Build composite dictionary key (LAT/LONG/LICENSEE)
        compositekey = float(row[0]),float(row[1]),str(row[2])
        # Check if key exists in dictionary already, and handle values accordingly (either create new dictionary key-value list pair or append value to existing value list)
        if compositekey in UniqueDict:
            UniqueDict[compositekey].append(row[3])
        else:
            UniqueDict[compositekey] = [row[3]]

# Create list of objectIDs we're going to delete
OIDToDelete = []
# Iterate through dictionary, grab all non-first objectIDs for each dictionary key and add to delete list
for k,v in UniqueDict.items():
    for row in v[1:]:
        OIDToDelete.append(row)

# Delete all records with ObjectIDs corresponding to those in the OIDToDelete List
with arcpy.da.UpdateCursor(pointdataset, "OBJECTID") as cursor:
    for row in cursor:
        if row[0] in OIDToDelete:
            cursor.deleteRow()