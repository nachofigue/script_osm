import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

project_dir = os.path.dirname(os.path.abspath(__file__))
# Usamos una nueva carpeta para la segunda cuenta
chrome_data_dir = os.path.join(project_dir, "chrome_data_2")

options = Options()
# detach = True mantiene el navegador abierto cuando el script termina
options.add_experimental_option("detach", True)
options.add_argument(f"user-data-dir={chrome_data_dir}")

# Nos aseguramos de que no haya otros chromes usando esta carpeta
os.system('taskkill /f /im chrome.exe /fi "COMMANDLINE eq *chrome_data_2*" >nul 2>&1')
time.sleep(2)

print("Abriendo navegador para la segunda cuenta...")
driver = webdriver.Chrome(options=options)

driver.get("https://es.onlinesoccermanager.com")
print("Por favor, inicia sesion en tu SEGUNDA cuenta en la ventana que se abrio.")
print("Una vez que hayas iniciado sesion y estes en el Dashboard, puedes cerrar la ventana del navegador.")
