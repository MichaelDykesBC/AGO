###=============================================================================================================================================
### AGO_AddFC.py
###     Written by: Michael Dykes
###     Created: 2019-08-06
###     Edited: 2019-08-30 (MDykes)
###
###     Purpose: Add Content to ArcGIS Online from File Geodatabase (Through GeoJSON)
###=============================================================================================================================================
from arcgis.gis import GIS
import arcpy, os, getpass

# Geodatabase Path
gdb = r'S:\Gis\Requests\First Nations Treaty Work\KitselasKitsumkalumAdditional\Geodatabase\KitselasKitsumkalum_Additional.gdb'

# Username and Password (echo-less) for ArcGIS Online (Not through IDIR)
username = input("Username :")
password = getpass.getpass(prompt='Password: ')

arcpy.env.workspace = gdb
arcpy.env.overwriteOutput = True

# Iterate Through Geodatabase Feature Classes
for fc in arcpy.ListFeatureClasses():
        print(fc)

        # Check for Empty Feature Classes
        if int(arcpy.GetCount_management(fc).getOutput(0)) != 0:
                # JSON FilePath & FileName & Extension (**Even if Title Property Below is Different, AGO Doesn't Accept Duplicate FileNames**)
                jsonfilepath = r"S:\Gis\Python\AGO\Python_Host\\" + "json_file" + fc + ".geojson"

                # Buid Feature Class Path for Input into Geoprocessing Tool
                FeatureClass = str(os.path.join(arcpy.env.workspace, fc))
                featurelayer = arcpy.MakeFeatureLayer_management(FeatureClass,"in_memory/featurelayer")
                geojsonfile = arcpy.FeaturesToJSON_conversion(featurelayer,jsonfilepath,geoJSON="GEOJSON")

                # Connect to GovernmentofBC AGO Portal
                gis = GIS('https://governmentofbc.maps.arcgis.com/',username,password)

                # Item Properties (Dictionary format), Type is Important for AGO to Recognize Data Format
                fc_toadd_properties = {'title': fc,'tags': 'AGRI', 'type': 'GeoJson'}

                # Set AGO Item Properties and Add Content (Can add 'folder=*foldername*' Parameter to Add Content Directly to Existing AGO Folder)
                fc_item = gis.content.add(item_properties=fc_toadd_properties, data=jsonfilepath)
                fc_layer = fc_item.publish()
                print("Published")

        # Delete JSON File
        os.remove(jsonfilepath)

print("Done")