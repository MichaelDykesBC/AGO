import os, time, requests, json, random
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

USER = os.getenv('GEOHUB_USERNAME')
PASSWORD = os.environ.get('GEOHUB_PASSWORD')

def random_data_entry():
    f = r'https://api.namefake.com/'
    data = requests.get(f)
    data.encoding = data.apparent_encoding
    return data.text

driver = webdriver.Chrome(r'D:\Users\Mike\Downloads\chromedriver_win32\chromedriver.exe')

driver.get("https://survey123.arcgis.com/share/b146efbdc2ca430a80d2ff39291e3c20?portalUrl=https://bcgov03.maps.arcgis.com")
time.sleep(5)

print(driver.title)

username = driver.find_element_by_name("username")
username.clear()
username.send_keys(USER)

password = driver.find_element_by_name("password")
password.clear()
password.send_keys(PASSWORD)

password.send_keys(Keys.RETURN)
time.sleep(5)

print(driver.title)

random_user_str = random_data_entry()
random_user = json.loads(random_user_str)

fullname = driver.find_element_by_name(r"/xls-b146efbdc2ca430a80d2ff39291e3c20/contact_information/first_and_last_name")
random_name = random_user['name']
fullname.send_keys(random_name)

y = random.randint(0,14)

x = random.randint(0,1)

if x == 0:
    driver.find_element(By.XPATH('//input[@id="idp47974016"]')).click()
else:
    driver.find_element(By.XPATH('//input[@id="idp47967184"]')).click()


print("Done")