from bs4 import BeautifulSoup
import bs4
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import selenium
import pandas as pd
import time
from selenium.webdriver.common.by import By


driver = webdriver.Chrome()
url = "https://www.starbucks.co.kr/store/store_map.do?disp=locale"
driver.get(url)
time.sleep(3)
links_selector = ""

driver.find_element(By.CSS_SELECTOR ,"ul.sido_arae_box > li > a").click()
time.sleep(3)
driver.find_element(By.CSS_SELECTOR , "ul.gugun_arae_box > li > a").click()
time.sleep(5)


html = driver.page_source
soup = BeautifulSoup(html, "html.parser")

data = []

all_store = soup.select("li.quickResultLstCon")
print(all_store)


for i in all_store:
    name = i.select("strong")[0].text.strip()
    lat = i["data-lat"]
    lng = i['data-long']
    address = str(i.select("p.result_details")[0]).split('<br/>')[0].split('>')[1]
    data.append([name,address,lat,lng])


columns = ['name','address','latitude', 'longitude']
csv = pd.DataFrame(data, columns = columns)
csv.to_csv("starbucks_crawl.csv", encoding='utf-8-sig', index=False)
