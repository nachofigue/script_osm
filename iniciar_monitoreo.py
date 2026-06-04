import time
import subprocess
import os

def main():
    project_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(project_dir, "reclamar_anuncios.py")
    
    # Intervalo de 1 hora y 10 minutos (70 minutos)
    interval_seconds = 70 * 60 
    
    print("=" * 60)
    print("       MONITOR DE RECLAMACIÓN DE ANUNCIOS DE OSM       ")
    print("=" * 60)
    print(f"El script se ejecutará cada 1 hora y 10 minutos (70 minutos).")
    print("Puedes detener este monitor presionando Ctrl + C en esta consola.\n")
    
    try:
        while True:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Iniciando proceso de reclamación de anuncios...")
            
            # Ejecutar el script principal
            result = subprocess.run(["python", script_path])
            
            print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Proceso finalizado.")
            print(f"Esperando 1 hora y 10 minutos para la siguiente ejecución...\n")
            
            # Dormir
            time.sleep(interval_seconds)
            
    except KeyboardInterrupt:
        print("\nMonitor detenido por el usuario (Ctrl + C). ¡Hasta luego!")

if __name__ == "__main__":
    main()
