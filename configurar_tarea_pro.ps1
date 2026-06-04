# Definir rutas
$scriptPath = "C:\Users\Ignacio\Desktop\script_osm\reclamar_anuncios.py"
$pythonPath = "C:\Users\Ignacio\AppData\Local\Microsoft\WindowsApps\python.exe"

# 1. Definir la acción (Ejecutar python reclamar_anuncios.py)
$action = New-ScheduledTaskAction -Execute $pythonPath -Argument $scriptPath

# 2. Definir los disparadores (Triggers)
# Disparador A: Al iniciar sesión el usuario actual (Ignacio)
$triggerLogon = New-ScheduledTaskTrigger -AtLogOn -User "$env:USERDOMAIN\$env:USERNAME"

# Disparador B: Repetición cada 70 minutos de forma indefinida
# Se inicia hoy en este momento
$triggerRepetitive = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 70) -RepetitionDuration (New-TimeSpan -Days 3650)

# 3. Definir la configuración de la tarea
# - AllowStartIfOnBatteries: Permite que corra si estás en laptop con batería
# - DontStopIfGoingOnBatteries: No se detiene si desconectas la energía
# - StartWhenAvailable: Ejecuta lo antes posible si se perdió una ejecución programada (PC apagada)
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# 4. Registrar la tarea en Windows
# Usamos el usuario actual para que corra de forma interactiva e invisible en tu sesión
$taskName = "OSM_Reclamar_Coins"
$user = "$env:USERDOMAIN\$env:USERNAME"

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $triggerLogon, $triggerRepetitive -Settings $settings -User $user -Force

Write-Host ""
Write-Host "=============================================================="
Write-Host " Tarea programada 'OSM_Reclamar_Coins' configurada con éxito."
Write-Host " Disparadores activos:"
Write-Host "  1. Al iniciar sesión en Windows (Logon)."
Write-Host "  2. Cada 70 minutos en bucle continuo."
Write-Host "  3. Ejecución inmediata si se omitió una tanda estando la PC apagada."
Write-Host "=============================================================="
