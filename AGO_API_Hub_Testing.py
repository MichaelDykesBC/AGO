import os, arcgis.apps
from arcgis.gis import GIS
from arcgishub import hub

AGO_URL = "https://bcgov03.maps.arcgis.com"
AGO_USERNAME = os.environ["GEOHUB_USERNAME"]
AGO_PASSWORD = os.environ["GEOHUB_PASSWORD"]

hub_initiative_itemid = "d8ebd2ce1a5e4bca88f6160a1a69362f"

#gis = GIS(url=AGO_URL,username=AGO_USERNAME,password=AGO_PASSWORD)
#hub_item = gis.content.get(hub_itemid)

myHub = hub.Hub(AGO_URL,username=AGO_USERNAME,password=AGO_PASSWORD)

#for row in myHub.initiatives.search():
#    print(row)

myInitiative = myHub.initiatives.get(hub_initiative_itemid)
mySite = myInitiative.site_id

site1 = myHub.sites.get(mySite)
print(site1)
print(site1.url)

for page in site1.pages.search():
    print(page)
    print(page.slug)
    #page.update(page_properties={'title':'Hub Site Gallery Page'})
    #page_data = page.get_data()

mySite_layout = site1.layout
mySite_header = site1.theme

print(mySite_header)

print(len(mySite_layout.sections))
for row in mySite_layout.sections:
    print(row)