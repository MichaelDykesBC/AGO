from arcgis.gis import GIS,ContentManager
import json, arcpy, os, getpass

username = input("Username :")
password = getpass.getpass(prompt='Password: ')

gis = GIS('https://governmentofbc.maps.arcgis.com/',username,password)

item = gis.content.search(query="owner:MDYKES.BC AND title:Land Analysis Web App Template", item_type="Web Mapping Application")[0]
print(item,item.id,item.url)

CManager = ContentManager(gis)

#print(CManager.create_folder("TESTING_Python"))
CManager.clone_items([item],"TESTING_Python")


'''
def _create_service(target, service_type, create_params=None, is_view=None, folder=None):
    """Create a new service.
    Keyword arguments:
    target - The instance of arcgis.gis.GIS (the portal) to create the service
    service_type - The type of service
    create_params - The service parameters
    is_view - Indicates if the service should be a view
    folder - the folder to create the service in"""
    
    portal = target._portal
    postdata = portal._postdata()
    owner = portal.logged_in_user()['username']

    # Setup the item path, including the folder, and post to it
    path = 'content/users/' + owner
    if folder and folder != '/':
        folder_id = portal.get_folder_id(owner, folder)
        path += '/' + folder_id
    path += '/createService'

    postdata['createParameters'] = [{'title':"Test"}]
    postdata['outputType'] = service_type
    #postdata['isView'] = is_view

    resp = portal.con.post(path, postdata)
    if resp and resp.get('success'):
        return target.content.get(resp['itemId'])
    return None

_create_service(gis,"Web Mapping Application")
'''

print("Done")