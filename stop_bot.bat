@echo off
echo Stopping Garmin Coach Telegram Bot...
powershell -Command "Get-Process python* | Where-Object { $_.CommandLine -like '*telegram_bot.py*' } | Stop-Process -Force"
echo [OK] Bot stopped successfully.
pause
