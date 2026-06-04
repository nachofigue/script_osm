from selenium import webdriver
import os
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def clean_up_chrome():
    print("Cerrando instancias de Chrome previas...")
    os.system('taskkill /f /im chrome.exe /fi "COMMANDLINE eq *chrome_data*" >nul 2>&1')
    time.sleep(2)

def get_coin_count(driver):
    """Obtiene la cantidad actual de monedas desde el wallet de la tienda."""
    try:
        wallet = driver.find_element(By.CSS_SELECTOR, ".bosscoin-wallet")
        text = wallet.text.strip().split('\n')[0].strip()
        return int(text)
    except:
        return -1

def wait_for_video_to_start(driver, timeout=15):
    """Espera a que aparezca un elemento <video> indicando que el anuncio empezó."""
    for _ in range(timeout):
        videos = driver.find_elements(By.TAG_NAME, "video")
        if len(videos) > 0:
            return True
        time.sleep(1)
    return False

def wait_for_video_to_finish(driver, timeout=45):
    """Espera a que desaparezcan los elementos <video> indicando que el anuncio terminó."""
    for _ in range(timeout):
        videos = driver.find_elements(By.TAG_NAME, "video")
        if len(videos) == 0:
            return True
        time.sleep(1)
    return False

def reclamar_anuncios(perfil="chrome_data"):
    wait_minutes = 70
    clean_up_chrome()
    
    options = Options()
    options.add_experimental_option("detach", False)
    
    project_dir = os.path.dirname(os.path.abspath(__file__))
    chrome_data_dir = os.path.join(project_dir, perfil)
    options.add_argument(f"user-data-dir={chrome_data_dir}")
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--mute-audio")
    
    driver = webdriver.Chrome(options=options)
    cookies_file = os.path.join(project_dir, "cookies.json")
    
    # 1. Cargar cookies
    driver.get("https://es.onlinesoccermanager.com")
    time.sleep(2)
    
    if os.path.exists(cookies_file):
        try:
            with open(cookies_file, "r") as f:
                cookies = json.load(f)
                for cookie in cookies:
                    # Normalizar expirationDate -> expiry
                    if 'expirationDate' in cookie:
                        cookie['expiry'] = int(cookie.pop('expirationDate'))
                    if cookie.get('expiry') is None:
                        cookie['expiry'] = int(time.time()) + 365 * 24 * 3600

                    # Eliminar campos que Selenium no acepta
                    for campo in ['hostOnly', 'session', 'storeId', 'sameSite']:
                        cookie.pop(campo, None)

                    try:
                        driver.add_cookie(cookie)
                    except:
                        pass
            print("Cookies de sesion cargadas.")
        except Exception as e:
            print("Error al cargar cookies:", e)
    
    # 2. Ir al Dashboard
    driver.get("https://es.onlinesoccermanager.com/Dashboard")
    time.sleep(6)
    
    if "/Career" in driver.current_url or "/carrera" in driver.current_url.lower():
        print("Estamos en Carrera. Seleccionando el primer club activo...")
        try:
            slots = driver.find_elements(By.CSS_SELECTOR, ".career-teamslot-container")
            for slot in slots:
                if "ELEGIR UN CLUB" not in slot.text.upper():
                    slot.click()
                    print("Club seleccionado. Esperando cargar Dashboard...")
                    time.sleep(6)
                    break
        except Exception as e:
            print("Error al seleccionar club:", e)
            
    timestamp = time.strftime('%H%M%S')
    driver.save_screenshot(os.path.join(project_dir, f"diagnostico/dashboard_{timestamp}.png"))
    
    # 3. Abrir la tienda UNA SOLA VEZ
    try:
        boss_coins_btn = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".bosscoin-wallet"))
        )
        boss_coins_btn.click()
        time.sleep(4)
    except Exception as e:
        print("No se pudo abrir la Tienda:", e)
        driver.quit()
        return wait_minutes
    
    # 4. Bucle de anuncios
    max_ads = 10
    ads_watched = 0
    
    for i in range(max_ads):
        print(f"\n--- Intento {i+1} ---")
        
        # Leer monedas ANTES del anuncio
        coins_before = get_coin_count(driver)
        print(f"Monedas antes: {coins_before}")
        
        # Buscar boton "Ver anuncio"
        try:
            btn = driver.find_element(By.CSS_SELECTOR, ".product-free")
            text = btn.text.strip().replace('\n', ' ')
            print(f"Texto del boton: '{text}'")
            
            if "Ver anuncio" not in text:
                print("El boton no muestra 'Ver anuncio'. Deteniendo.")
                break
            
            # Desplazar y hacer click
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'instant', block: 'center', inline: 'center'});", btn)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", btn)
            print("Click en 'Ver anuncio' realizado.")
            
        except Exception as e:
            print(f"No se encontro el boton: {e}")
            break
        
        # Esperar 3 segundos para verificar popup de limite
        time.sleep(3)
        
        popups = driver.find_elements(By.XPATH, "//*[contains(text(), 'No se puede mostrar') or contains(text(), 'máximo de vídeos')]")
        if len(popups) > 0:
            print("Limite alcanzado. Cerrando aviso...")
            popup_text = popups[0].text
            body_text = driver.find_element(By.TAG_NAME, "body").text
            import re
            match = re.search(r'(\d+)\s*minutos', body_text)
            if match:
                detected_mins = int(match.group(1))
                wait_minutes = detected_mins + 1
                print(f"Detectado tiempo de espera en el popup: {detected_mins} minutos. Se esperaran {wait_minutes} minutos.")
            else:
                print("No se detecto el numero de minutos en el aviso. Se usara el tiempo por defecto.")
            try:
                ok_btn = driver.find_element(By.XPATH, "//*[text()='Ok' or text()='OK']")
                driver.execute_script("arguments[0].click();", ok_btn)
            except:
                pass
            break
        
        # Esperar a que el video empiece
        print("Esperando a que el video empiece...")
        video_started = wait_for_video_to_start(driver, timeout=10)
        
        if not video_started:
            time.sleep(15)
            coins_after = get_coin_count(driver)
            if coins_after > coins_before:
                ads_watched += 1
                print(f"Anuncio contado sin video visible. Total reclamadas: {ads_watched}")
            else:
                print("El video NO empezo y no se acreditaron monedas.")
            continue
        
        print("Video detectado. Esperando a que termine...")
        
        # Esperar a que el video termine
        video_finished = wait_for_video_to_finish(driver, timeout=45)
        
        if not video_finished:
            print("El video no termino en 45 segundos. Continuando de todos modos.")
        else:
            print("Video terminado.")
        
        # Esperar 5 segundos adicionales para que se acredite la recompensa
        time.sleep(5)
        
        # Verificar que las monedas aumentaron
        coins_after = get_coin_count(driver)
        print(f"Monedas despues: {coins_after}")
        
        if coins_after > coins_before:
            gain = coins_after - coins_before
            ads_watched += 1
            print(f"Recompensa confirmada: +{gain} moneda(s). Total reclamadas: {ads_watched}")
        else:
            print("Las monedas NO aumentaron. Este anuncio no dio recompensa.")
        
        # Esperar un poco antes del siguiente intento
        time.sleep(2)
        
        # Desplazar la tienda hacia el boton de "Ver anuncio" nuevamente
        try:
            btn_next = driver.find_element(By.CSS_SELECTOR, ".product-free")
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'instant', block: 'center', inline: 'center'});", btn_next)
            time.sleep(1)
        except:
            print("No se encontro el boton 'Ver anuncio' para el siguiente intento.")
            break
    
    print(f"\nProceso terminado. Anuncios reclamados con exito: {ads_watched}")
    driver.quit()
    return wait_minutes

# --- BLOQUE PRINCIPAL MODIFICADO ---
if __name__ == "__main__":
    print("=== Iniciando Bot de Reclamación Automática ===")
    
    cuentas = ["chrome_data_2"]
    while True:
        minutos_espera = 70
        try:
            print(f"\n[+] Iniciando ciclo de reclamación: {time.strftime('%H:%M:%S')}")
            for cuenta in cuentas:
                print(f"\n=====================================")
                print(f"  Procesando cuenta: {cuenta}")
                print(f"=====================================")
                tiempo_obtenido = reclamar_anuncios(cuenta)
                if tiempo_obtenido:
                    minutos_espera = tiempo_obtenido
        except Exception as e:
            print(f" Ocurrió un error inesperado en el ciclo principal: {e}")
            print("Se reintentará en el próximo turno.")
        
        print(f"\n[-] Ciclo finalizado. Esperando {minutos_espera} minutos para el siguiente...")
        
        # Un pequeño bucle visual para saber cuánto tiempo le queda en la consola
        for restante in range(minutos_espera, 0, -1):
            print(f"Próxima ejecución en: {restante} minutos...", end="\r")
            time.sleep(60) # Espera 1 minuto antes de restar el siguiente contador