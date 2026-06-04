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
    
    # 5. Esperar a que cargue la tienda
    time.sleep(5)
    
    # 6. Buscar el botón "Ver anuncio" (.product-free)
    print("Buscando el botón 'Ver anuncio'...")
    ver_anuncio_btn = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".product-free"))
    )
    
    # 7. Desplazar el elemento para que sea visible (horizontalmente)
    print("Desplazando hacia el elemento...")
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center', inline: 'center'});", ver_anuncio_btn)
    time.sleep(2)
    
    # 8. Hacer click de forma robusta con JavaScript
    print("¡Haciendo click en 'Ver anuncio'!")
    driver.execute_script("arguments[0].click();", ver_anuncio_btn)
    
    # 9. Esperar a que se cargue el anuncio o ventana emergente
    time.sleep(10)
    
    # Tomar captura de pantalla
    screenshot_path = os.path.join(project_dir, "ad_screenshot.png")
    driver.save_screenshot(screenshot_path)
    print(f"Captura de pantalla guardada en: {screenshot_path}")
    print("URL actual:", driver.current_url)

except Exception as e:
    print("Ocurrió un error:", e)

print("\nScript ejecutado. Navegador abierto.")
