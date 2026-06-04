import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

project_dir = os.path.dirname(os.path.abspath(__file__))
chrome_data_dir = os.path.join(project_dir, "chrome_data_2")

options = Options()
options.add_argument(f"user-data-dir={chrome_data_dir}")

os.system('taskkill /f /im chrome.exe /fi "COMMANDLINE eq *chrome_data_2*" >nul 2>&1')
time.sleep(2)

driver = webdriver.Chrome(options=options)
driver.get("https://es.onlinesoccermanager.com/Career")
time.sleep(8)

html = driver.page_source
with open(os.path.join(project_dir, "carrera_html.txt"), "w", encoding="utf-8") as f:
    f.write(html)
    
driver.save_screenshot(os.path.join(project_dir, "carrera.png"))
driver.quit()
print("HTML y captura de pantalla guardados.")
