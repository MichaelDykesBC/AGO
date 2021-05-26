import getpass, urllib, json, requests
from requests.auth import HTTPBasicAuth

username = "MDYKES.BC"
password = getpass.getpass(prompt='Password: ')

def generateToken(username, password, portalUrl):
    '''Retrieves a token to be used with API requests.'''
    parameters = urllib.urlencode({'username' : username,
                                   'password' : password,
                                   'client' : 'referer',
                                   'referer': portalUrl,
                                   'expiration': 120,
                                   'f' : 'json'})
    response = urllib.urlopen(portalUrl + '/sharing/rest/generateToken?',
                              parameters).read()
    try:
        jsonResponse = json.loads(response)
        if 'token' in jsonResponse:
            return jsonResponse['token']
        elif 'error' in jsonResponse:
            print(jsonResponse['error']['message'])
            for detail in jsonResponse['error']['details']:
                print(detail)
    except ValueError, e:
        print('An unspecified error occurred.')
        print(e)

#apikeyStr = generateToken(username,password,'https://governmentofbc.maps.arcgis.com/')

# Server + Function using
# APIServer = r'https://governmentofbc.maps.arcgis.com/sharing/content/users/' + username + r'/addItem'
APIServer = r'https://governmentofbc.maps.arcgis.com/sharing/rest/content/users/' + username + r'/addItem'
#auth = HTTPBasicAuth('apikey', apikeyStr)

params = {'URL':'https://governmentofbc.maps.arcgis.com/','title':'Test Mapping Application','type':'Web Mapping Application','tags':'TEST'}

response = requests.get(APIServer,params=params)
status = response.status_code

if status == 200:
    print("Good")
    #print(response.json())
    #data = response.json()['features'][0]['geometry']['coordinates']
    #siteid = response.json()['features'][0]['properties']['siteID']

else:
    print("Bad: " + status)

print("Done")