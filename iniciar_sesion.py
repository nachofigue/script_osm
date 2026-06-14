import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

project_dir = os.path.dirname(os.path.abspath(__file__))

options = Options()
# Conectar al Chrome que el usuario ya abrió mediante el .bat
options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

print("Intentando conectar al navegador abierto en el puerto 9222...")
try:
    # No usamos undetected-chromedriver aquí, usamos el selenium normal
    # porque ya estamos conectados a un navegador 100% real y humano.
    driver = webdriver.Chrome(options=options)
except Exception as e:
    print("---------------------------------------------------------")
    print("ERROR: No se pudo conectar a Chrome.")
    print("¿Aseguraste de ejecutar 'iniciar_chrome_debug.bat' primero?")
    print("Recuerda que debes cerrar TODOS los Chrome antes de usar el .bat")
    print("---------------------------------------------------------")
    exit(1)

driver.get("https://es.onlinesoccermanager.com")
print("Por favor, inicia sesion en tu cuenta de OSM.")
print("Como estás usando tu navegador normal, no debería detectarte como bot.")
print("")
input(">>> PRESIONA ENTER AQUI EN LA CONSOLA CUANDO HAYAS TERMINADO Y QUIERAS DESCONECTAR EL BOT <<<")

# Al usar Remote Debugging, salir del script solo desconecta el bot,
# el navegador se quedará abierto y tu sesión guardada.

