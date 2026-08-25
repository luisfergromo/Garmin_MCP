@echo off
echo Deteniendo Garmin Coach Telegram Bot...
powershell -Command "Get-Process python* | Where-Object { $_.CommandLine -like '*telegram_bot.py*' } | Stop-Process -Force"
echo [OK] Bot detenido.
pause
