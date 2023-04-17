import os
from arcgis.gis import GIS, User
from neo4j import GraphDatabase

GeoHub_USER = os.getenv('GEOHUB_USERNAME')
GeoHub_PASSWORD = os.environ.get('GEOHUB_PASSWORD')

neo4j_password = os.environ.get('NEO4J_PASSWORD')

URI = "bolt://localhost:7687"
AUTH = ("neo4j", neo4j_password)

def clear_database(tx):
    tx.run("MATCH (n) DETACH DELETE n")

def create_user(tx, name):
    user_object = User(gis, name)
    user_type = None
    try:
        if user_object.categories:
            if "Proxy Account" in user_object.categories[0]:
                user_type = "PROXY"
            elif "BIER" in user_object.categories[0]:
                user_type = "BIER"
            elif "Named User" in user_object.categories[0]:
                user_type = "NAMED"
    except:
        pass
    if user_type:
        tx.run("MERGE (user:USER:" + user_type + " {name: $name, role: $role})", name=name, role=user_type)
    else:
        tx.run("MERGE (user:USER {name: $name, role: $role})", name=name, role="None")

def create_group(tx, name, access, created, protected):
    tx.run("MERGE (group:GROUP:" + access.upper() + " {name: $name, created:$created, delete_protection:$protected})", name=name, access=access, created=created, protected=protected)

def create_member_of(tx, name, group_name):
    tx.run("MATCH (user:USER {name: $name}),(group:GROUP {name: $group_name}) "
           "CREATE (user) - [:MEMBER_OF] -> (group)", name=name, group_name=group_name)
    
def create_manager_of(tx, name, group_name):
    tx.run("MATCH (user:USER {name: $name}),(group:GROUP {name: $group_name}) "
           "CREATE (user) - [:MANAGER_OF] -> (group)", name=name, group_name=group_name)

def create_owner_of(tx, name, group_name):
    tx.run("MATCH (user:USER {name: $name}),(group:GROUP {name: $group_name}) "
           "CREATE (user) - [:OWNER_OF] -> (group)", name=name, group_name=group_name)

gis = GIS("https://bcgov03.maps.arcgis.com",username=GeoHub_USER,password=GeoHub_PASSWORD)
all_groups = gis.groups.search(max_groups=9000)

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    with driver.session() as session:
        session.execute_write(clear_database)
        n = 0
        for group in all_groups:
            print(group)
            group_protected = group.protected
            group_access = group.access
            group_created = group.created
            session.execute_write(create_group, group.title, group_access, group_created, group_protected)

            members = group.get_members()
            users = members['users']
            for user in users:
                session.execute_write(create_user, user)
                session.execute_write(create_member_of, user, group.title)

            admins = members['admins']
            for user in admins:
                session.execute_write(create_user, user)
                session.execute_write(create_manager_of, user, group.title)

            owner = members['owner']
            session.execute_write(create_user, user)
            session.execute_write(create_owner_of, user, group.title)
            n += 1
print(n)