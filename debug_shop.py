import os
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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

try:
    # 4. Abrir la tienda
    print("Abriendo tienda...")
    boss_coins_btn = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".bosscoin-wallet"))
    )
    boss_coins_btn.click()
    
    # Esperar a que cargue la tienda
    time.sleep(5)
    
    print("\n--- Buscando elementos de 'Ver anuncio' o 'GRATIS' en la Tienda ---")
    
    # Buscamos por texto o selectores genéricos
    elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'anuncio') or contains(text(), 'Anuncio') or contains(text(), 'GRATIS') or contains(text(), 'Gratis')]")
    
    for i, el in enumerate(elements):
        try:
            text = el.text.strip().replace('\n', ' ')
            tag = el.tag_name
            classes = el.get_attribute("class")
            id_attr = el.get_attribute("id")
            print(f"[{i}] Tag: <{tag}>, ID: '{id_attr}', Class: '{classes}', Text: '{text}'")
        except Exception as e:
            pass
            
    # Intentamos buscar también elementos que tengan clases o atributos que parezcan botones de video/anuncio
    video_elements = driver.find_elements(By.CSS_SELECTOR, "*[class*='video'], *[class*='ad'], *[class*='free'], *[class*='watch']")
    print("\n--- Elementos sospechosos por clase (video/ad/free/watch) ---")
    for i, el in enumerate(video_elements):
        try:
            text = el.text.strip().replace('\n', ' ')
            tag = el.tag_name
            classes = el.get_attribute("class")
            print(f"[{i}] Tag: <{tag}>, Class: '{classes}', Text: '{text}'")
        except:
            pass

except Exception as e:
    print("Error:", e)

print("\nBúsqueda finalizada.")
