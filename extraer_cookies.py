import os
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

project_dir = os.path.dirname(os.path.abspath(__file__))
chrome_data_dir = os.path.join(project_dir, "chrome_data_2")

options = Options()
options.add_argument(f"user-data-dir={chrome_data_dir}")
options.add_argument("--headless=new")

print("Cerrando Chrome previo si lo hubiera...")
os.system('taskkill /f /im chrome.exe >nul 2>&1')
time.sleep(2)

print("Iniciando navegador para extraer cookies...")
driver = webdriver.Chrome(options=options)

driver.get("https://es.onlinesoccermanager.com")
time.sleep(5)

cookies = driver.get_cookies()

with open(os.path.join(project_dir, "cookies.json"), "w") as f:
    json.dump(cookies, f, indent=4)

print(f"¡Exito! Se extrajeron {len(cookies)} cookies y se guardaron en cookies.json")
driver.quit()
