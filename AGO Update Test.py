from datetime import datetime
from arcgis.gis import GIS
from pytz import timezone

gis = GIS("https://bcgov03.maps.arcgis.com",username="michael.dykes_bcgov03",password="!Edinburgh1")

Layer = gis.content.get("d55467efe0e746aeb13e35338279a8e4")
print(Layer)

created_time = datetime.utcfromtimestamp(Layer.created/1000).astimezone(timezone('US/Pacific')).strftime('%Y-%m-%d')
modified_time = datetime.utcfromtimestamp(Layer.modified/1000).astimezone(timezone('US/Pacific')).strftime('%Y-%m-%d')

try:
    data_modified = max([i.properties.editingInfo.lastEditDate for i in Layer.layers + Layer.tables])
    data_modified_time = datetime.utcfromtimestamp(data_modified/1000).astimezone(timezone('US/Pacific')).strftime('%Y-%m-%d')
except:
    data_modified_time = None

print(Layer.title,Layer.type,Layer.id,Layer.url,Layer.shared_with,Layer.owner,Layer.numViews,created_time,modified_time,data_modified_time)

'''
data = Layer.layers[0].query(where="eventid=150009")
print(data)
edit = data.features[0]
edit.attributes['shakemapurl'] = 'Test'

Layer.layers[0].edit_features(updates=[edit])


Interface_list = []

subsection = soup.find('div',{"class":"portlet-content"})
wildfiretable = subsection.find('table')
wildfires = wildfiretable.find_all('tr')
for row in wildfires:
    if row.find('img',{"alt":"Interface"}):
        if "\xa0" in row.findAll(text=True)[1]:
            wildfireid = row.findAll(text=True)[1].replace("xa0","").strip()
            Interface_list.append(wildfireid)
        else:
            wildfireid = str(row.findAll(text=True)[1].strip())
            Interface_list.append(wildfireid)
'''