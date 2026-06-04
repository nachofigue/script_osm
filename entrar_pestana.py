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
    # 4. Esperar a que el botón de Boss Coins esté visible y hacer click
    print("Esperando al botón de Boss Coins (.bosscoin-wallet)...")
    boss_coins_btn = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".bosscoin-wallet"))
    )
    
    print("¡Botón encontrado! Haciendo click...")
    boss_coins_btn.click()
    
    # 5. Esperar a que cargue la nueva sección
    time.sleep(5)
    
    # Tomar captura de pantalla
    screenshot_path = os.path.join(project_dir, "store_screenshot.png")
    driver.save_screenshot(screenshot_path)
    print(f"Captura de la pestaña abierta guardada en: {screenshot_path}")
    print("URL actual:", driver.current_url)

except Exception as e:
    print("Ocurrió un error al buscar o hacer click en el botón:", e)

print("\nScript ejecutado. Navegador abierto.")
