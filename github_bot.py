import os
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_coin_count(driver):
    try:
        wallet = driver.find_element(By.CSS_SELECTOR, ".bosscoin-wallet")
        text = wallet.text.strip().split('\n')[0].strip()
        return int(text)
    except:
        return -1

def wait_for_video_to_start(driver, timeout=15):
    for _ in range(timeout):
        videos = driver.find_elements(By.TAG_NAME, "video")
        if len(videos) > 0: return True
        time.sleep(1)
    return False

def wait_for_video_to_finish(driver, timeout=45):
    for _ in range(timeout):
        videos = driver.find_elements(By.TAG_NAME, "video")
        if len(videos) == 0: return True
        time.sleep(1)
    return False

def run_github_bot():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--mute-audio")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    project_dir = os.path.dirname(os.path.abspath(__file__))
    driver = webdriver.Chrome(options=options)
    cookies_file = os.path.join(project_dir, "cookies.json")
    
    print("Accediendo a OSM para inyectar sesión...")
    driver.get("https://es.onlinesoccermanager.com")
    time.sleep(2)
    
    if os.path.exists(cookies_file):
        with open(cookies_file, "r") as f:
            cookies = json.load(f)
        for cookie in cookies:
            if 'expirationDate' in cookie: cookie['expiry'] = int(cookie.pop('expirationDate'))
            if cookie.get('expiry') is None: cookie['expiry'] = int(time.time()) + 365*24*3600
            for campo in ['hostOnly', 'session', 'storeId', 'sameSite']: cookie.pop(campo, None)
            try: driver.add_cookie(cookie)
            except: pass
        print("Cookies cargadas.")
    else:
        print("ERROR: No se encontro el archivo cookies.json")
        driver.quit()
        return
        
    driver.get("https://es.onlinesoccermanager.com/Dashboard")
    time.sleep(6)
    
    if "/Career" in driver.current_url or "/carrera" in driver.current_url.lower():
        print("Estamos en Carrera. Seleccionando club...")
        try:
            slots = driver.find_elements(By.CSS_SELECTOR, ".career-teamslot-container")
            for slot in slots:
                if "ELEGIR UN CLUB" not in slot.text.upper():
                    slot.click()
                    time.sleep(6)
                    break
        except Exception as e: print(e)
            
    if "/Dashboard" not in driver.current_url:
        print("Fallo el login o no hay Dashboard. Saliendo.")
        driver.quit()
        return
        
    try:
        boss_coins_btn = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".bosscoin-wallet")))
        boss_coins_btn.click()
        time.sleep(4)
    except:
        print("No se pudo abrir la tienda")
        driver.quit()
        return
        
    ads_watched = 0
    for i in range(10):
        coins_before = get_coin_count(driver)
        print(f"Intento {i+1} | Monedas: {coins_before}")
        
        try:
            btn = driver.find_element(By.CSS_SELECTOR, ".product-free")
            if "Ver anuncio" not in btn.text.replace('\n', ' '): break
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'instant', block: 'center', inline: 'center'});", btn)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", btn)
        except: break
        
        time.sleep(3)
        if len(driver.find_elements(By.XPATH, "//*[contains(text(), 'No se puede mostrar') or contains(text(), 'máximo de vídeos')]")) > 0:
            print("Límite alcanzado.")
            break
            
        if not wait_for_video_to_start(driver, 10):
            time.sleep(15)
            if get_coin_count(driver) > coins_before: ads_watched += 1
            continue
            
        wait_for_video_to_finish(driver, 45)
        time.sleep(5)
        
        if get_coin_count(driver) > coins_before:
            ads_watched += 1
            print("Recompensa confirmada!")
            
        time.sleep(2)
        try:
            btn_next = driver.find_element(By.CSS_SELECTOR, ".product-free")
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'instant', block: 'center', inline: 'center'});", btn_next)
            time.sleep(1)
        except: break

    print(f"Proceso finalizado. Total reclamados: {ads_watched}")
    driver.quit()

if __name__ == "__main__":
    run_github_bot()
