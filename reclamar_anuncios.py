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
    
    project_dir = os.path.dirname(os.path.abspath(__file__))
    chrome_data_dir = os.path.join(project_dir, perfil)
    
    import subprocess
    is_visible = os.environ.get("OSM_VISIBLE")
    
    if is_visible:
        print("Iniciando navegador en modo VISIBLE...")
    else:
        print("Iniciando navegador fantasma (invisible) y silenciado...")
        
    cmd = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        "--remote-debugging-port=9222",
        f"--user-data-dir={chrome_data_dir}",
        "--mute-audio",
        "--log-level=3" # Esto oculta los errores basura internos de Chrome (como el DEPRECATED_ENDPOINT)
    ]
    
    if not is_visible:
        cmd.append("--headless=new")
        subprocess.Popen(cmd, creationflags=0x08000000)
    else:
        subprocess.Popen(cmd)
        
    time.sleep(4) # Darle tiempo a que abra y exponga el puerto
    
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    
    try:
        driver = webdriver.Chrome(options=options)
    except Exception as e:
        print("No se pudo conectar a Chrome:", e)
        return wait_minutes
    
    print("Cargando página principal de OSM (Autologin activo)...")
    driver.get("https://es.onlinesoccermanager.com/")
    time.sleep(8) # Dar tiempo a que cargue y redireccione automáticamente a la Carrera
    
    # Elegir Club directamente (ya que estamos en la Carrera)
    print("Eligiendo club...")
    try:
        # Busca el enlace al Dashboard del primer slot activo o botón de Jugar
        club_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/Dashboard')]")
        if len(club_links) > 0:
            driver.execute_script("arguments[0].click();", club_links[0])
            print("-> Club seleccionado.")
        else:
            # Alternativa: Botones comunes de entrar al club
            club_btn = driver.find_element(By.XPATH, "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'jugar') or contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'continuar')]")
            driver.execute_script("arguments[0].click();", club_btn)
            print("-> Club seleccionado (botón genérico).")
    except Exception as e:
        print("-> No se pudo hacer clic en el club. Forzando navegación al Dashboard por URL...")
        driver.get("https://es.onlinesoccermanager.com/Dashboard")
        
    time.sleep(8) # Dar tiempo a que cargue el Dashboard completamente
            
    print(f"URL actual (Dashboard): {driver.current_url}")
    timestamp = time.strftime('%H%M%S')
    
    # Si la carpeta diagnostico no existe, la creamos para que no de error la foto
    if not os.path.exists(os.path.join(project_dir, "diagnostico")):
        os.makedirs(os.path.join(project_dir, "diagnostico"))
        
    driver.save_screenshot(os.path.join(project_dir, f"diagnostico/dashboard_{timestamp}.png"))
    
    # 5. Abrir la tienda UNA SOLA VEZ
    try:
        boss_coins_btn = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".bosscoin-wallet"))
        )
        boss_coins_btn.click()
        time.sleep(4)
        print(f"URL actual tras abrir Tienda: {driver.current_url}")
    except Exception as e:
        print("No se pudo abrir la Tienda:", e)
        driver.quit()
        return wait_minutes
    
    # 4. Bucle de anuncios
    max_ads = 10
    ads_watched = 0
    
    for i in range(max_ads):
        print(f"\n--- Intento {i+1} ---")
        print(f"URL actual en la tienda: {driver.current_url}")
        
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
            print("Limite alcanzado. Analizando aviso...")
            body_text = driver.find_element(By.TAG_NAME, "body").text
            import re
            
            # Buscar dígitos seguidos de la palabra minuto/s
            match_mins = re.search(r'(\d+)\s*minuto', body_text, re.IGNORECASE)
            # Buscar menciones a "una hora" o "1 hora"
            match_hora = re.search(r'(una|1)\s*hora', body_text, re.IGNORECASE)
            
            if match_mins:
                detected_mins = int(match_mins.group(1))
                wait_minutes = detected_mins + 1
                print(f"-> Se detectaron {detected_mins} minutos en el aviso. El bot esperará {wait_minutes} minutos.")
            elif match_hora:
                wait_minutes = 61
                print("-> Se detectó '1 hora' en el aviso. El bot esperará 61 minutos.")
            else:
                wait_minutes = 61
                print("-> No se reconoció el tiempo exacto en el texto. Por seguridad, el bot esperará 61 minutos.")
                
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
    clean_up_chrome() # Cerramos el navegador real para liberar memoria durante los 70 minutos de espera
    return wait_minutes

# --- BLOQUE PRINCIPAL MODIFICADO ---
if __name__ == "__main__":
    print("=== Iniciando Bot de Reclamación Automática ===")
    
    cuentas = ["chrome_data"]
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