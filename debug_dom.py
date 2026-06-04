import os
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

options = Options()
options.add_experimental_option("detach", True)

# Directorio de datos
project_dir = os.path.dirname(os.path.abspath(__file__))
chrome_data_dir = os.path.join(project_dir, "chrome_data")
options.add_argument(f"user-data-dir={chrome_data_dir}")

driver = webdriver.Chrome(options=options)

cookies_file = os.path.join(project_dir, "cookies.json")

# 1. Establecer el dominio
driver.get("https://es.onlinesoccermanager.com")
time.sleep(2)

# 2. Cargar cookies
if os.path.exists(cookies_file):
    try:
        with open(cookies_file, "r") as f:
            cookies = json.load(f)
        for cookie in cookies:
            if cookie.get('expiry') is None:
                cookie['expiry'] = int(time.time()) + 365 * 24 * 3600
            try:
                driver.add_cookie(cookie)
            except:
                pass
    except Exception as e:
        print("Error al cargar cookies:", e)

# 3. Ir al Dashboard
driver.get("https://es.onlinesoccermanager.com/Dashboard")
time.sleep(8)  # Dar tiempo para cargar completamente

# Tomar captura de pantalla
screenshot_path = os.path.join(project_dir, "dashboard_screenshot.png")
driver.save_screenshot(screenshot_path)
print(f"Captura de pantalla guardada en: {screenshot_path}")

# Buscar elementos que puedan ser el botón de Boss Coins
print("\n--- Buscando elementos de monedas/compras en el DOM ---")

# Vamos a buscar selectores comunes
selectors = [
    "*[class*='coin']",
    "*[class*='bosscoin']",
    "*[class*='currency']",
    "*[id*='coin']",
    "*[id*='bosscoin']",
    "*[class*='store']",
    "*[class*='shop']",
    "button",
    "a"
]

found_elements = []
for selector in selectors:
    try:
        elements = driver.find_elements(By.CSS_SELECTOR, selector)
        for el in elements:
            try:
                text = el.text.strip()
                tag = el.tag_name
                classes = el.get_attribute("class")
                id_attr = el.get_attribute("id")
                
                # Buscamos elementos que tengan el texto "55" o "+" o contengan "coin"
                if text == "55" or "+" in text or "coin" in classes.lower() or "bosscoin" in classes.lower():
                    info = {
                        "tag": tag,
                        "class": classes,
                        "id": id_attr,
                        "text": text,
                        "selector_origin": selector
                    }
                    if info not in found_elements:
                        found_elements.append(info)
            except:
                pass
    except Exception as e:
        pass

for i, el in enumerate(found_elements):
    print(f"[{i}] Tag: <{el['tag']}>, ID: '{el['id']}', Class: '{el['class']}', Text: '{el['text']}' (vía {el['selector_origin']})")

print("\nBúsqueda completada.")
