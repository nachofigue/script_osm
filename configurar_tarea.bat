@echo off
set PYTHON_PATH=C:\Users\Ignacio\AppData\Local\Microsoft\WindowsApps\py.exe
set SCRIPT_PATH=C:\Users\Ignacio\Desktop\script_osm\reclamar_anuncios.py

schtasks /create /tn "OSM_Reclamar_Coins" /tr "\"%PYTHON_PATH%\" \"%SCRIPT_PATH%\"" /sc onlogon /delay 0001:00 /it /f

echo.
echo Tarea programada 'OSM_Reclamar_Coins' configurada con exito.
echo.
pause