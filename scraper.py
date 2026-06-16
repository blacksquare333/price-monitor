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
options.add_argument("--disable-blink-features=AutomationControlled")   
options.add_experimental_option("excludeSwitches", ["enable-automation"])

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)

all_laptops = []
supabase_buffer = []

try:
    for page in range(0,5):
        url = f"https://th.aliexpress.com/w/wholesale-laptop.html?spm=a2g0o.home.search.{page}"
        try:
            time.sleep(random.uniform(1,3))
            driver.get(url)
            wait = WebDriverWait(driver, 10)
            element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,"h3.lk_kx")))
            for _ in range(3):
                driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
                time.sleep(random.uniform(1,1.5))
        except Exception as e:
            print(f"错误:{url}:{e}")
            continue

        titles = driver.find_elements(By.CSS_SELECTOR,"div.lk_z")   
        prices = driver.find_elements(By.CSS_SELECTOR,"div.lk_lg") 

        for title,price in zip(titles,prices):
            all_laptops.append({"title":title.text, "price":price.text})
            supabase_buffer.append({"titles":title.text, "prices":price.text})      
            print(title.text, price.text)  

    if supabase_buffer:
        supabase_client.table("price-monitor").insert(supabase_buffer).execute() 
        print(f"批量导入{len(supabase_buffer)}条数据")         

    df = pd.DataFrame(all_laptops)
    df.to_excel('laptops.xlsx',index=False)

finally:
    driver.quit()
