import glob, os, csv
from PIL import Image
from arcgis.gis import GIS

def compress_big(image_file):
    im = Image.open(image_file)
    print(im.size[0],(int(im.size[0]*0.10),int(im.size[1]*0.10)))
    im2 = im.convert('RGB')
    image = im2.resize((int(im.size[0]*0.10),int(im.size[1]*0.10)))
    print(os.path.basename(f1).split(".")[0])
    newfile = r"C:\Users\Mike\Desktop\ClimateReadyBC_NewImages\\" + os.path.basename(f1).split(".")[0] + ".jpg" 
    image.save(newfile, "JPEG", optimize = True, quality = 95)
    return newfile

def compress_medium2(image_file):
    im = Image.open(image_file)
    print(im.size[0],(int(im.size[0]*0.20),int(im.size[1]*0.20)))
    im2 = im.convert('RGB')
    image = im2.resize((int(im.size[0]*0.20),int(im.size[1]*0.20)))
    newfile = r"C:\Users\Mike\Desktop\ClimateReadyBC_NewImages\\" + os.path.basename(f1).split(".")[0] + ".jpg" 
    image.save(newfile, "JPEG", optimize = True, quality = 95)
    return newfile

def compress_medium(image_file):
    im = Image.open(image_file)
    print(im.size[0],(int(im.size[0]*0.50),int(im.size[1]*0.50)))
    im2 = im.convert('RGB')
    image = im2.resize((int(im.size[0]*0.50),int(im.size[1]*0.50)))
    newfile = r"C:\Users\Mike\Desktop\ClimateReadyBC_NewImages\\" + os.path.basename(f1).split(".")[0] + ".jpg" 
    image.save(newfile, "JPEG", optimize = True, quality = 95)
    return newfile

def compress(image_file):
    im = Image.open(image_file)
    image = im.convert('RGB')
    newfile = r"C:\Users\Mike\Desktop\ClimateReadyBC_NewImages\\" + os.path.basename(f1).split(".")[0] + ".jpg" 
    image.save(newfile, "JPEG", optimize = True, quality = 95)
    return newfile

PORTAL_URL = "https://bcgov03.maps.arcgis.com"
PORTAL_USERNAME = os.getenv('GEOHUB_USERNAME')
PORTAL_PASSWORD = os.environ.get('GEOHUB_PASSWORD')

gis = GIS(PORTAL_URL, username=PORTAL_USERNAME, password=PORTAL_PASSWORD, expiration=9999)

img_dir = r"C:\Users\Mike\Desktop\ClimateReadyBC Images"
data_path = os.path.join(img_dir,'*g') 
files = glob.glob(data_path) 
data = []
with open(r"C:\Users\Mike\Desktop\ClimateReadyBC_Images.csv", 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile, delimiter=',')
    csvwriter.writerow(["TITLE","ITEM_URL"])
    for f1 in files:
        print(f1)
        file_size = os.path.getsize(f1)
        newfile = compress(f1)
        TOU = """<p style="margin-top:0px; margin-bottom:1.55rem; font-family:&quot;Avenir Next W01&quot;, &quot;Avenir Next W00&quot;, &quot;Avenir Next&quot;, Avenir, &quot;Helvetica Neue&quot;, sans-serif; font-size:17px;"><font size="2"><span style="font-family:&quot;Avenir Next W01&quot;, &quot;Avenir Next W00&quot;, &quot;Avenir Next&quot;, Avenir, &quot;Helvetica Neue&quot;, Helvetica, Arial, sans-serif;">Licensed under </span><a href="https://www2.gov.bc.ca/gov/content/home/copyright" style="color:rgb(0, 121, 193); text-decoration-line:none; font-family:&quot;Avenir Next W01&quot;, &quot;Avenir Next W00&quot;, &quot;Avenir Next&quot;, Avenir, &quot;Helvetica Neue&quot;, Helvetica, Arial, sans-serif;">Access Only</a>.<br /></font></p><p style="margin-top:0px; margin-bottom:1.55rem; font-family:&quot;Avenir Next W01&quot;, &quot;Avenir Next W00&quot;, &quot;Avenir Next&quot;, Avenir, &quot;Helvetica Neue&quot;, sans-serif; font-size:17px;"><font size="2">These data are</font><font size="2"> <a href="https://www2.gov.bc.ca/gov/content/home/copyright" style="color:rgb(0, 121, 193); text-decoration-line:none;">Copyright © Province of British Columbia</a>. All rights reserved.<br /></font></p><p style="margin-top:0px; margin-bottom:1.55rem; font-family:&quot;Avenir Next W01&quot;, &quot;Avenir Next W00&quot;, &quot;Avenir Next&quot;, Avenir, &quot;Helvetica Neue&quot;, sans-serif; font-size:17px;"><font size="2">The EM GeoHUB and associated materials, including map applications (&quot;Maps&quot;), trade-marks and official marks (collectively, &quot;Materials&quot;), are owned or used under license by the Province of British Columbia (&quot;Province&quot;) and are protected by copyright and trade-mark laws. Please see the <a href="https://www2.gov.bc.ca/gov/content/governments/about-the-bc-government/databc/geographic-data-and-services/agol/access-and-use-constraints" style="color:rgb(0, 121, 193); text-decoration-line:none;">Disclaimer</a> for further details.</font></p><p style="margin-top:0px; margin-bottom:1.55rem; font-family:&quot;Avenir Next W01&quot;, &quot;Avenir Next W00&quot;, &quot;Avenir Next&quot;, Avenir, &quot;Helvetica Neue&quot;, sans-serif; font-size:17px;"><font size="2">The Province does not collect, use or disclose personal information through the ArcGIS Online website. Please be aware, however, that IP addresses are collected by Esri and are stored on Esri's servers located outside of Canada. For further information, including the purposes for which your IP address is collected, please see Esri's Privacy Policy at: <a style="color:rgb(0, 121, 193);">https://www.esri.com/en-us/privacy/privacy-statements/privacy-statement</a>. By accessing or using the EM GeoHUB, you consent, effective as of the date of such access or use, to Esri storing and accessing your IP address outside of Canada for the purposes described in Esri's Privacy Policy. </font></p>"""
        desc = """Image used in <a href="https://climatereadybc.gov.bc.ca/">https://climatereadybc.gov.bc.ca/</a>"""
        snippet = os.path.basename(f1).split(".")[0] + " image used in ClimateReadyBC"
        img_properties ={"title":os.path.basename(f1).split(".")[0],"type":"Image","licenseInfo":TOU,"accessInformation":"Province of British Columbia","description":desc,"snippet":snippet}

        mycontent = gis.content.search(query="title: " + str(os.path.basename(f1).split(".")[0]) + " owner:michael.dykes_bcgov03")
        print(mycontent)
        for item in mycontent:
            if item.title == os.path.basename(f1).split(".")[0]:
                item.update(item_properties=img_properties, data=newfile)
                item.share(everyone=True)
                item.protect(enable = True)
                print(item)

        #img_item = gis.content.add(item_properties=img_properties, data=newfile, folder="ClimateReadyBC")
        #img_item.share(everyone=True)
        #img_item.protect(enable = True)
        #csvwriter.writerow([os.path.basename(f1).split(".")[0],img_item.url]) 