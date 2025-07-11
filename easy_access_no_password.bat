@echo off
echo 🌍 EASY ACCESS - No Password Required!
echo.

REM Kill any existing LocalTunnel
taskkill /f /im node.exe >nul 2>&1

REM Start Django server if not running
echo 🚀 Starting Django server...
start /B python manage.py runserver 8000

REM Wait for server
timeout /t 3 /nobreak > nul

REM Use different tunnel service (no password)
echo 🌐 Creating password-free tunnel...
echo.
echo ✅ This tunnel won't require any password!
echo 📱 Share the URL directly with anyone!
echo.

REM Use serveo (no password required)
ssh -R 80:localhost:8000 serveo.net

pause
