import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
# Mantiene el navegador abierto al finalizar el script
options.add_experimental_option("detach", True)

# Definimos la ruta de datos de Chrome directamente dentro del proyecto para evitar conflictos y que sea visible
project_dir = os.path.dirname(os.path.abspath(__file__))
chrome_data_dir = os.path.join(project_dir, "chrome_data")
options.add_argument(f"user-data-dir={chrome_data_dir}")

# Iniciamos el navegador
driver = webdriver.Chrome(options=options)

import json

cookies_file = os.path.join(project_dir, "cookies.json")

# 1. Navegamos primero a la página base para establecer el dominio en el navegador
driver.get("https://es.onlinesoccermanager.com")
time.sleep(2)

# 2. Intentamos cargar las cookies guardadas
if os.path.exists(cookies_file):
    try:
        with open(cookies_file, "r") as f:
            cookies = json.load(f)
        for cookie in cookies:
            # Si la cookie es de sesión (Expiry es None), le damos 1 año de vida
            if cookie.get('expiry') is None:
                cookie['expiry'] = int(time.time()) + 365 * 24 * 3600
            # Algunas cookies pueden fallar si tienen un formato no compatible, las agregamos con try-catch
            try:
                driver.add_cookie(cookie)
            except Exception as cookie_err:
                pass
        print("Cookies de sesión cargadas desde cookies.json.")
    except Exception as e:
        print("Error al cargar las cookies:", e)

# 3. Navegamos al Dashboard
driver.get("https://es.onlinesoccermanager.com/Dashboard")

# 4. Verificamos si logramos entrar al Dashboard directamente
time.sleep(5)
current_url = driver.current_url

if "/Dashboard" in current_url:
    print("\n¡Sesión iniciada correctamente en el Dashboard!")
    # Guardamos las cookies actualizadas
    try:
        with open(cookies_file, "w") as f:
            json.dump(driver.get_cookies(), f)
        print("Cookies guardadas/actualizadas.")
    except Exception as e:
        print("Error al guardar cookies:", e)
else:
    print("\nNo se detectó sesión activa. Por favor, inicia sesión manualmente en la ventana abierta...")
    
    # Esperamos hasta 120 segundos para que el usuario inicie sesión
    logged_in = False
    for _ in range(24):
        if "/Dashboard" in driver.current_url:
            logged_in = True
            break
        time.sleep(5)
        
    if logged_in:
        print("\n¡Inicio de sesión detectado!")
        # Guardamos las nuevas cookies
        try:
            with open(cookies_file, "w") as f:
                json.dump(driver.get_cookies(), f)
            print("Cookies guardadas para futuros inicios automáticos.")
        except Exception as e:
            print("Error al guardar cookies:", e)
    else:
        print("\nTiempo de espera agotado sin iniciar sesión.")

print("\n¡Navegador listo!")