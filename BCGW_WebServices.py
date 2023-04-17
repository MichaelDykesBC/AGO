# Import required libraries/modules
import requests

Resturl = r'https://maps.gov.bc.ca/arcserver/rest/services/whse'
response = requests.get(Resturl + '?f=json')
sitejson = response.json()

for service in sitejson['services']:
    print(service)
    url = r'https://maps.gov.bc.ca/arcserver/rest/services/whse' + r"/" + service['name'] + r"/MapServer" 
    print(url)
    response2 = requests.get(url + '?f=json')
    sitejson2 = response2.json()
    print(sitejson2)