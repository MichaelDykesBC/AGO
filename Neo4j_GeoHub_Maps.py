import os, getpass, requests
from datetime import datetime
from arcgis.gis import GIS, User
from arcgis.mapping import WebMap
from neo4j import GraphDatabase

GeoHub_USER = os.getenv('GEOHUB_USERNAME')
GeoHub_PASSWORD = os.environ.get('GEOHUB_PASSWORD')

neo4j_password = os.environ.get('NEO4J_PASSWORD')

URI = "bolt://localhost:7687"
AUTH = ("neo4j", neo4j_password)

def clear_database(tx):
    tx.run("MATCH (n) DETACH DELETE n")

def create_layer(tx, url, name):
    tx.run("MERGE (layer:LAYER {url: $url, name: $name})", url=url,name=name)

def create_map(tx, name, created, protected):
    tx.run("MERGE (map:WEBMAP {name: $name, created:$created, delete_protection:$protected})", name=name, created=created, protected=protected)

def create_layer_of(tx, url, map_name):
    tx.run("MATCH (layer:LAYER {url: $url}),(map:WEBMAP {name: $map_name}) "
           "CREATE (layer) - [:LAYER_OF] -> (map)", url=url, map_name=map_name)

gis = GIS("https://bcgov03.maps.arcgis.com",username=GeoHub_USER,password=GeoHub_PASSWORD)
token = gis._con.token
all_maps = gis.content.search(query="*",item_type="Web Map",max_items=9999)

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    with driver.session() as session:
        session.execute_write(clear_database)
        n = 0
        for map in all_maps:
            map_title = map.title
            print(map_title)
            created_epoch = int(map.created)
            map_created = created_epoch
            protected = map.protected
            session.execute_write(create_map, map_title, map_created, protected)
            webmap = WebMap(map)
            for layer in webmap.layers:
                # if layers in layer then group layer, need to iterate through that for url and title
                if "url" in layer:
                    url = layer['url']
                    access_url = url + "?f=pjson&token=" + token
                    try:
                        x = requests.get(access_url)
                        layer_data = x.json()
                        layer_name = layer_data['name']
                        geometry_type = layer_data['geometryType']
                        last_edit_date = layer_data['editingInfo']['lastEditDate']
                    except:
                        layer_name = layer['title']
                    session.execute_write(create_layer, url, layer_name)
                    session.execute_write(create_layer_of, url, map_title)
                else:
                    print("*",layer)
            n += 1
print(n)