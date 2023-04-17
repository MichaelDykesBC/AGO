import os
import win32com.client
from arcgis.gis import GIS

filelocation = r'C:\Users\Mike\Desktop'

PORTAL_URL = "https://bcgov03.maps.arcgis.com"
PORTAL_USERNAME = os.getenv('GEOHUB_USERNAME')
PORTAL_PASSWORD = os.environ.get('GEOHUB_PASSWORD')
gis = GIS(PORTAL_URL,PORTAL_USERNAME,PORTAL_PASSWORD)

dashboard_itemID = "f4c4f169aa15497a9f300b42fb175d44"
dashboard_item = gis.content.get(dashboard_itemID)
dashboard_data = dashboard_item.get_data()

Func = open(filelocation + "\\DashboardTest.html","w")
for widget in dashboard_data["widgets"]:
    if "text" in widget:
        Func.write(widget["text"])
Func.close()

word = win32com.client.Dispatch('Word.Application')

doc = word.Documents.Add(filelocation + "\\DashboardTest.html")
doc.SaveAs(filelocation + '\\example.doc', FileFormat=0)
doc.Close()

word.Quit()