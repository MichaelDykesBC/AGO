from arcgis.gis import GIS
import json, arcpy, os, getpass

username = input("Username :")
password = getpass.getpass(prompt='Password: ')

gis = GIS('https://governmentofbc.maps.arcgis.com/',username,password)

#ContentManager = arcgis.gis.ContentManager(gis)
#testdict = {"Type:Web Mapping Application"}
#print(ContentManager.add(testdict))

item = gis.content.search(query="owner:MDYKES.BC AND title:Land Analysis Web App Template", item_type="Web Mapping Application")[0]
print(item,item.id,item.url)

if item:
    WebApp_JSON_File = r'S:\Gis\Python\AGO\Map Base JSON\WebApp_JSON.txt'

    item_data = item.get_data()
    with open(WebApp_JSON_File, 'w') as outfile:
        json.dump(item_data, outfile)

class _ItemDefinition(object):
    """
    Represents the definition of an item within ArcGIS Online or Portal.
    """

    def __init__(self, info, data=None, sharing=None, thumbnail=None, portal_item=None):
        self.info = info
        self._data = data    
        self.sharing = sharing
        if not self.sharing:
            self.sharing = {"access": "private", "groups": []}
        self.thumbnail = thumbnail
        self._item_property_names = ['title', 'type', 'description', 
                                     'snippet', 'tags', 'culture',
                                     'accessInformation', 'licenseInfo', 'typeKeywords', 'extent']
        self.portal_item = portal_item

    @property
    def data(self):
        """Gets the data of the item"""
        return copy.deepcopy(self._data)

    def _get_item_properties(self):
        """Get a dictionary of item properties used in create and update operations."""

        item_properties = {}
        for property_name in self._item_property_names:
            item_properties[property_name] = self.info[property_name]

        type_keywords = item_properties['typeKeywords']
        for keyword in list(type_keywords):
            if keyword.startswith('source-'):
                type_keywords.remove(keyword)

        tags = item_properties['tags']

        tags.extend(ADD_TAGS)
        expressions = [re.compile(x) for x in REMOVE_TAGS]
        item_properties['tags'] = [t for t in tags if all(not ex.match(t) for ex in expressions)]
        if _TARGET_MUST_EXIST_TAG in item_properties['tags']:
            item_properties['tags'].remove(_TARGET_MUST_EXIST_TAG)
        if _MAINTAIN_SPATIAL_REF in item_properties['tags']:
            item_properties['tags'].remove(_MAINTAIN_SPATIAL_REF)
        if _COPY_ONLY_TAG in item_properties['tags']:
            item_properties['tags'].remove(_COPY_ONLY_TAG)

        type_keywords.append('source-{0}'.format(self.info['id']))
        item_properties['typeKeywords'] = ','.join(item_properties['typeKeywords'])
        item_properties['tags'] = ','.join(item_properties['tags'])

        extent = _deep_get(item_properties, 'extent')
        if ITEM_EXTENT is not None and extent is not None and len(extent) > 0:
            item_properties['extent'] = ITEM_EXTENT

        return item_properties

    def clone(self, target, folder, item_mapping):  
        """Clone the item in the target organization.
        Keyword arguments:
        target - The instance of arcgis.gis.GIS (the portal) to clone the item to.
        folder - The folder to create the item in
        item_mapping - Dictionary containing mapping between new and old items.
        """
    
        try:
            new_item = None
            original_item = self.info
        
            # Get the item properties from the original item to be applied when the new item is created
            item_properties = self._get_item_properties()

            temp_dir = os.path.join(_TEMP_DIR.name, original_item['id'])
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)

            data = self.data
            if not data and self.portal_item:
                data = self.portal_item.download(temp_dir)
                
            # The item's name will default to the name of the data, if it already exists in the folder we need to rename it to something unique
            name = os.path.basename(data)
            item = next((item for item in target.users.me.items(folder=_deep_get(folder, 'title')) if item['name'] == name), None)
            if item:
                new_name = "{0}_{1}{2}".format(os.path.splitext(name)[0], str(uuid.uuid4()).replace('-', ''), os.path.splitext(name)[1])
                new_path = os.path.join(temp_dir, new_name)
                os.rename(data, new_path)
                data = new_path

            thumbnail = self.thumbnail
            if not thumbnail and self.portal_item:
                thumbnail = self.portal_item.download_thumbnail(temp_dir)

            # Add the new item
            new_item = target.content.add(item_properties=item_properties, data=data, thumbnail=thumbnail, folder=_deep_get(folder, 'title'))

            return [new_item]
        except Exception as ex:
            raise _ItemCreateException("Failed to create {0} {1}: {2}".format(original_item['type'], original_item['title'], str(ex)), new_item)

class _TextItemDefinition(_ItemDefinition):
    """
    Represents the definition of a text based item within ArcGIS Online or Portal.
    """

    def clone(self, target, folder, item_mapping):  
        """Clone the item in the target organization.
        Keyword arguments:
        target - The instance of arcgis.gis.GIS (the portal) to clone the item to.
        folder- The folder to create the item in
        item_mapping - Dictionary containing mapping between new and old items.
        """
    
        try:
            new_item = None
            original_item = self.info
        
            # Get the item properties from the original item to be applied when the new item is created
            item_properties = self._get_item_properties()
            data = self.data
            if data:
                item_properties['text'] = json.dumps(data)

            thumbnail = self.thumbnail
            if not thumbnail and self.portal_item:
                temp_dir = os.path.join(_TEMP_DIR.name, original_item['id'])
                if not os.path.exists(temp_dir):
                    os.makedirs(temp_dir)
                thumbnail = self.portal_item.download_thumbnail(temp_dir)
            new_item = target.content.add(item_properties=item_properties, thumbnail=thumbnail, folder=_deep_get(folder, 'title'))

            return [new_item]
        except Exception as ex:
            raise _ItemCreateException("Failed to create {0} {1}: {2}".format(original_item['type'], original_item['title'], str(ex)), new_item)

class _ApplicationDefinition(_TextItemDefinition):
    """
    Represents the definition of an application within ArcGIS Online or Portal.
    """
    
    def __init__(self, info, source_app_title=None, update_url=True, data=None, sharing=None, thumbnail=None, portal_item=None):
        self._source_app_title = source_app_title
        self._update_url = update_url
        super().__init__(info, data, sharing, thumbnail, portal_item)

    @property
    def source_app_title(self):
        """Gets the title of the application"""
        return self._source_app_title

    @property
    def update_url(self):
        """Gets a value indicating if the application url should be updated"""
        return self._update_url

    def clone(self, target, folder, item_mapping):
        """Clone the application in the target organization.
        Keyword arguments:
        target - The instance of arcgis.gis.GIS (the portal) to clone the web map to
        folder - The folder to create the item in
        item_mapping - Dictionary containing mapping between new and old items.     
        """  

        new_item = None
        original_item = self.info
        org_url = _get_org_url(target)
        is_web_appbuilder = False

        # Get the item properties from the original application which will be applied when the new item is created
        item_properties = self._get_item_properties()

        # Swizzle the item ids of the web maps, groups and URLs of defined in the application's data
        app_json = self.data
        if app_json is not None:
            app_json_text = ''
            
            # If item is a story map don't swizzle any of the json references
            if 'Story Map' in original_item['typeKeywords'] or 'Story Maps' in original_item['typeKeywords']:
                app_json_text = json.dumps(app_json)

            else:
                if "Web AppBuilder" in original_item['typeKeywords']: #Web AppBuilder
                    is_web_appbuilder = True
                    if 'portalUrl' in app_json:
                        app_json['portalUrl'] = org_url
                    if 'map' in app_json:
                        if 'portalUrl' in app_json['map']:
                            app_json['map']['portalUrl'] = org_url
                        if 'itemId' in app_json['map']:
                            app_json['map']['itemId'] = item_mapping['Item IDs'][app_json['map']['itemId']]
                        if 'mapOptions' in app_json['map'] and app_json['map']['mapOptions'] is not None:
                            if 'extent' in app_json['map']['mapOptions']:
                                del app_json['map']['mapOptions']['extent']
                    if 'httpProxy' in app_json:
                        if 'url' in app_json['httpProxy']:
                            app_json['httpProxy']['url'] = org_url + "sharing/proxy"
                    if 'geometryService' in app_json and 'geometry' in target.properties['helperServices']:
                        app_json['geometryService'] = target.properties['helperServices']['geometry']['url']

                elif original_item['type'] in ["Operation View", "Dashboard"]: #Operations Dashboard
                    if 'widgets' in app_json:
                        for widget in app_json['widgets']:
                            if widget['type'] == 'mapWidget':
                                if 'itemId' in widget:
                                    widget['itemId'] = item_mapping['Item IDs'][widget['itemId']]
                                elif 'mapId' in widget:
                                    widget['mapId'] = item_mapping['Item IDs'][widget['mapId']]

                else: #Configurable Application Template
                    if 'folderId' in app_json:
                        app_json['folderId'] = _deep_get(folder, 'id')
                    if 'values' in app_json:
                        if 'group' in app_json['values']:
                            app_json['values']['group'] = item_mapping['Group IDs'][app_json['values']['group']]
                        if 'webmap' in app_json['values']:
                            if isinstance(app_json['values']['webmap'], list):
                                new_webmap_ids = []
                                for webmap_id in app_json['values']['webmap']:
                                    new_webmap_ids.append(item_mapping['Item IDs'][webmap_id])
                                app_json['values']['webmap'] = new_webmap_ids
                            else:
                                app_json['values']['webmap'] = item_mapping['Item IDs'][app_json['values']['webmap']]
                    if self.source_app_title is not None:
                        search_query = 'title:"{0}" AND owner:{1} AND type:Web Mapping Application'.format(self.source_app_title, "esri_en") 
                        search_items = target.content.search(search_query, max_items=100, outside_org=True)
                        if len(search_items) > 0:
                            existing_item = max(search_items, key=lambda x: x['created'])
                            app_json['source'] = existing_item['id']

                app_json_text = json.dumps(app_json)        
                for original_url in item_mapping['Feature Services']:
                    service = item_mapping['Feature Services'][original_url]
                    for key, value in service['layer_id_mapping'].items():
                        app_json_text = re.sub("{0}/{1}".format(original_url, key), 
                                                "{0}/{1}".format(service['url'], value),
                                                app_json_text, 0, re.IGNORECASE)
                    app_json_text = re.sub(original_url, service['url'], app_json_text, 0, re.IGNORECASE)
                for original_id in item_mapping['Item IDs']:
                    app_json_text = re.sub(original_id, item_mapping['Item IDs'][original_id], app_json_text, 0, re.IGNORECASE)

                # Replace any references to default print service
                new_print_url = _deep_get(target.properties, 'helperServices', 'printTask', 'url')
                if new_print_url is not None:
                    old_print_url = 'https://utility.arcgisonline.com/arcgis/rest/services/Utilities/PrintingTools/GPServer/Export%20Web%20Map%20Task'
                    if self.portal_item is not None and _deep_get(self.portal_item._gis.properties, 'helperServices', 'printTask', 'url') is not None:
                        old_print_url = _deep_get(self.portal_item._gis.properties, 'helperServices', 'printTask', 'url')

                    app_json_text = re.sub(old_print_url, new_print_url, app_json_text, 0, re.IGNORECASE)
                    if old_print_url.startswith('https://'):
                        app_json_text = re.sub('http://' + old_print_url[8:], new_print_url, app_json_text, 0, re.IGNORECASE)
                    elif old_print_url.startswith('http://'):
                        app_json_text = re.sub('https://' + old_print_url[7:], new_print_url, app_json_text, 0, re.IGNORECASE)

                # Perform a general find and replace of field names if field mapping is required
                for service in item_mapping['Feature Services']:
                    for layer_id in item_mapping['Feature Services'][service]['layer_field_mapping']:
                        field_mapping = item_mapping['Feature Services'][service]['layer_field_mapping'][layer_id]
                        app_json_text = _find_and_replace_fields(app_json_text, field_mapping)

            # Replace any references to the original org url with the target org url. Used to re-point item resource references
            if original_item['url'] is not None:
                url = original_item['url']
                find_string = "/apps/"
                index = url.find(find_string)
                if index != -1:
                    source_org_url = url[:index+1]
                    app_json_text = re.sub(source_org_url, org_url, app_json_text, 0, re.IGNORECASE)

            item_properties['text'] = app_json_text

        # Add the application to the target portal
        thumbnail = self.thumbnail
        if not thumbnail and self.portal_item:
            temp_dir = os.path.join(_TEMP_DIR.name, original_item['id'])
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            thumbnail = self.portal_item.download_thumbnail(temp_dir)
        new_item = target.content.add(item_properties=item_properties, thumbnail=thumbnail, folder=_deep_get(folder, 'title'))

        # Add the resources to the new item
        if self.portal_item:
            resources = self.portal_item.resources
            resource_list = resources.list()
            if len(resource_list) > 0:
                resources_dir = os.path.join(_TEMP_DIR.name, original_item['id'], 'resources')
                if not os.path.exists(resources_dir):
                    os.makedirs(resources_dir)
                for resource in resource_list:
                    resource_path = resources.get(resource['resource'], False, resources_dir)
                    folder_name = None
                    resource_name = resource['resource']
                    if len(resource_name.split('/')) == 2:
                        folder_name, resource_name = resource_name.split('/')
                    new_item.resources.add(resource_path, folder_name, resource_name)

        # Update the url of the item to point to the new portal and new id of the application if required
        if original_item['url'] is not None:
            url = original_item['url']
            if self.update_url:
                find_string = "/apps/"
                index = original_item['url'].find(find_string)
                url = '{0}{1}'.format(org_url.rstrip('/'), original_item['url'][index:])
                find_string = "id="
                index = url.find(find_string)
                url = '{0}{1}'.format(url[:index + len(find_string)], new_item.id)
            item_properties = {'url' : url}
            new_item.update(item_properties)

        # Add a code attachment if the application is Web AppBuilder so that it can be downloaded
        if is_web_appbuilder:
            url = '{0}sharing/rest/content/items/{1}/package'.format(org_url[org_url.find('://') + 1:], new_item['id'])
            code_attachment_properties = {'title' : new_item['title'], 'type' : 'Code Attachment', 'typeKeywords' : 'Code,Web Mapping Application,Javascript',
                                            'relationshipType' : 'WMA2Code', 'originItemId' : new_item['id'], 'url' : url }
            target.content.add(item_properties=code_attachment_properties, folder=_deep_get(folder, 'title'))

        return [new_item]


def _get_item_definition(item):
    """Get an instance of the corresponding definition class for the specified item. This definition can be used to clone or download the item.
    Keyword arguments:
    item - The arcgis.GIS.Item to get the definition for.
    """  
       
    # If the item is an application or dashboard get the ApplicationDefinition
    if item['type'] in ['Web Mapping Application', 'Operation View', 'Dashboard']:
        app_json = None
        source_app_title = None
        update_url = False
        
        try:
            app_json = item.get_data()
        except Exception:
            pass # item doesn't have json data

        if app_json is not None:
            update_url = True
            if "Web AppBuilder" not in item['typeKeywords'] and item['type'] != 'Operation View' and 'source' in app_json:
                try:
                    source = item._gis
                    source_id = app_json['source']
                    app_item = source.content.get(source_id)
                    if app_item is not None:
                        source_app_title = app_item['title']
                except Exception:
                    pass

        return _ApplicationDefinition(dict(item), source_app_title=source_app_title, update_url=update_url, data=app_json, thumbnail=None, portal_item=item)

print(_get_item_definition(item))
print("Done")