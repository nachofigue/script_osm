import os
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

project_dir = os.path.dirname(os.path.abspath(__file__))
chrome_data_dir = os.path.join(project_dir, "chrome_data")
screenshots_dir = os.path.join(project_dir, "diagnostico")
os.makedirs(screenshots_dir, exist_ok=True)

options = Options()
options.add_experimental_option("detach", False)
options.add_argument(f"user-data-dir={chrome_data_dir}")
options.add_argument("--headless=new")
options.add_argument("--window-size=1920,1080")
options.add_argument("--mute-audio")

# Limpiar Chrome anterior
os.system('taskkill /f /im chrome.exe /fi "COMMANDLINE eq *chrome_data*" >nul 2>&1')
time.sleep(2)

driver = webdriver.Chrome(options=options)
cookies_file = os.path.join(project_dir, "cookies.json")

# Cargar cookies
driver.get("https://es.onlinesoccermanager.com")
time.sleep(2)

if os.path.exists(cookies_file):
    with open(cookies_file, "r") as f:
        cookies = json.load(f)
    for cookie in cookies:
        if cookie.get('expiry') is None:
            cookie['expiry'] = int(time.time()) + 365 * 24 * 3600
        try:
            driver.add_cookie(cookie)
        except:
            pass

# Ir al Dashboard
driver.get("https://es.onlinesoccermanager.com/Dashboard")
time.sleep(6)

driver.save_screenshot(os.path.join(screenshots_dir, "01_dashboard.png"))
print(f"URL Dashboard: {driver.current_url}")

# Abrir tienda
boss_coins_btn = WebDriverWait(driver, 15).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, ".bosscoin-wallet"))
)

# Capturar cantidad de monedas actual
wallet_text = boss_coins_btn.text.strip()
print(f"Monedas actuales (texto del wallet): '{wallet_text}'")

boss_coins_btn.click()
time.sleep(4)

driver.save_screenshot(os.path.join(screenshots_dir, "02_tienda_abierta.png"))

# Intentar ver 1 solo anuncio con diagnóstico completo
btn = driver.find_element(By.CSS_SELECTOR, ".product-free")
text = btn.text.strip().replace('\n', ' ')
print(f"Texto del boton: '{text}'")

driver.execute_script("arguments[0].scrollIntoView({behavior: 'instant', block: 'center', inline: 'center'});", btn)
time.sleep(1)
driver.save_screenshot(os.path.join(screenshots_dir, "03_boton_visible.png"))

print("Haciendo click en 'Ver anuncio'...")
driver.execute_script("arguments[0].click();", btn)

# Tomar capturas cada 5 segundos durante 35 segundos
for sec in range(7):
    wait = 5
    time.sleep(wait)
    elapsed = (sec + 1) * wait
    screenshot_name = f"04_despues_click_{elapsed}s.png"
    driver.save_screenshot(os.path.join(screenshots_dir, screenshot_name))
    
    # Verificar si hay popup de error
    popups = driver.find_elements(By.XPATH, "//*[contains(text(), 'No se puede mostrar') or contains(text(), 'máximo de vídeos')]")
    
    # Verificar URL actual
    current_url = driver.current_url
    
    # Verificar si hay un iframe de video/anuncio
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    
    # Verificar si hay un elemento de video
    videos = driver.find_elements(By.TAG_NAME, "video")
    
    print(f"  [{elapsed}s] URL: {current_url} | Popups error: {len(popups)} | Iframes: {len(iframes)} | Videos: {len(videos)}")

# Captura final
driver.save_screenshot(os.path.join(screenshots_dir, "05_estado_final.png"))
print(f"\nURL final: {driver.current_url}")

# Verificar monedas después
try:
    driver.get("https://es.onlinesoccermanager.com/Dashboard")
    time.sleep(5)
    boss_coins_btn2 = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".bosscoin-wallet"))
    )
    wallet_text_after = boss_coins_btn2.text.strip()
    print(f"Monedas despues: '{wallet_text_after}'")
    driver.save_screenshot(os.path.join(screenshots_dir, "06_monedas_despues.png"))
except Exception as e:
    print(f"Error al verificar monedas: {e}")

driver.quit()
print(f"\nCapturas guardadas en: {screenshots_dir}")
