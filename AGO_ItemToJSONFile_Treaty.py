from arcgis.gis import GIS
from arcgis.mapping import WebMap
import json, arcpy, getpass

username = input("Username :")
password = getpass.getpass(prompt='Password: ')

gis = GIS('https://governmentofbc.maps.arcgis.com/',username,password)

item_search = gis.content.search(query="owner:MDYKES.BC AND title:Web Map Template", item_type="Web Map")

if item_search:
   if len(item_search) == 1:
      item = item_search[0]
   else:
      for row in item_search:
         if row['title'] == "Web Map Template":
            item = row

if item:
   ALR_JSON_File = r'S:\Gis\Python\AGO\Map Base JSON\ALR_JSON.txt'
   AgCAP_JSON_File = r'S:\Gis\Python\AGO\Map Base JSON\AgCapability_JSON.txt'
   PMBC_JSON_File = r'S:\Gis\Python\AGO\Map Base JSON\PMBC_JSON.txt'
   CrownTenureAll_File = r'S:\Gis\Python\AGO\Map Base JSON\CrownTenureAll_JSON.txt'
   CrownTenureAquaculture_File = r'S:\Gis\Python\AGO\Map Base JSON\CrownTenureAquaculture_JSON.txt'
   RangeTenure_File = r'S:\Gis\Python\AGO\Map Base JSON\RangeTenure_JSON.txt'
   RangePasture_File = r'S:\Gis\Python\AGO\Map Base JSON\RangePasture_JSON.txt'
   SoilSurvey_File = r'S:\Gis\Python\AGO\Map Base JSON\SoilSurvey_JSON.txt'
   LivestockLarge_File = r'S:\Gis\Python\AGO\Map Base JSON\LivestockLarge_JSON.txt'
   IndianReserves_File = r'S:\Gis\Python\AGO\Map Base JSON\IndianReserves_JSON.txt'
   Greenspace_File = r'S:\Gis\Python\AGO\Map Base JSON\Greenspace_JSON.txt'
   BCParks_File = r'S:\Gis\Python\AGO\Map Base JSON\BCParks_JSON.txt'
   NationalParks_File = r'S:\Gis\Python\AGO\Map Base JSON\NationalParks_JSON.txt'

   item_data = item.get_data()
   for row in item_data['operationalLayers']:
      if row['title'] == 'Agricultural Land Reserve':
         with open(ALR_JSON_File, 'w') as outfile:
            json.dump(row, outfile)

      if row['title'] == 'Agricultural Capability':
         with open(AgCAP_JSON_File, 'w') as outfile:
            json.dump(row, outfile)

      if row['title'] == 'ParcelMap BC Parcel Fabric':
         with open(PMBC_JSON_File, 'w') as outfile:
            json.dump(row, outfile)

      if row['title'] == 'Crown Tenures (All)':
         with open(CrownTenureAll_File, 'w') as outfile:
            json.dump(row, outfile)

      if row['title'] == 'Crown Tenures - Aquaculture':
         with open(CrownTenureAquaculture_File, 'w') as outfile:
            json.dump(row, outfile)

      if row['title'] == 'Range Tenure':
         with open(RangeTenure_File, 'w') as outfile:
            json.dump(row, outfile)

      if row['title'] == 'Range Pastures':
         with open(RangePasture_File, 'w') as outfile:
            json.dump(row, outfile)

      if row['title'] == 'Soil Survey':
         with open(SoilSurvey_File, 'w') as outfile:
            json.dump(row, outfile)

      if row['title'] == 'Livestock at Large Regulations':
         with open(LivestockLarge_File, 'w') as outfile:
            json.dump(row, outfile)

      if row['title'] == 'Indian Reserves':
         with open(IndianReserves_File, 'w') as outfile:
            json.dump(row, outfile)

      if row['title'] == 'Local and Regional Greenspaces':
         with open(Greenspace_File, 'w') as outfile:
            json.dump(row, outfile)

      if row['title'] == 'BC Parks, Ecological Reserves, and Protected Areas':
         with open(BCParks_File, 'w') as outfile:
            json.dump(row, outfile)

      if row['title'] == 'National Parks of Canada within British Columbia':
         with open(NationalParks_File, 'w') as outfile:
            json.dump(row, outfile)

print("Done")