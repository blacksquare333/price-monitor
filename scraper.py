from supabase import create_client
from dotenv import load_dotenv
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd 
import time
import random

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-blink-features=AutomationControlled")   
options.add_experimental_option("excludeSwitches", ["enable-automation"])
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)

all_laptops = []

for page in range(0,5):
    url = f"https://th.aliexpress.com/w/wholesale-laptop.html?spm=a2g0o.home.search.{page}"
    try:
        time.sleep(random.uniform(1,3))
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,"h3.lk_kx")))
    except Exception as e:
        print(f"错误 :{url}:{e}")
        continue
 
    
    titles = driver.find_elements(By.CSS_SELECTOR,"h3.lk_kx")   
    prices = driver.find_elements(By.CSS_SELECTOR,"div.lk_lg") 

    for title,price in zip(titles,prices):
        all_laptops.append({"title":title.text, "price":price.text})
        supabase_client.table("price-monitor").insert({"titles":title.text, "prices":price.text}).execute()    
        print(title.text, price.text)           

   


df = pd.DataFrame(all_laptops)
df.to_excel('laptops.xlsx',index=False)

driver.quit()
