@echo off
echo 🚀 RUPP Room Booking System - Local Network Server
echo ============================================================

REM Get local IP address
for /f "delims=[] tokens=2" %%a in ('ping -4 -n 1 %ComputerName% ^| findstr [') do set NetworkIP=%%a

echo 🌐 Your Local IP Address: %NetworkIP%
echo 🔗 Server URL: http://%NetworkIP%:8000
echo.
echo ⚠️  IMPORTANT REQUIREMENTS:
echo    • Your computer must stay ON and running this server
echo    • Phone and computer must be on the SAME WiFi network  
echo    • This only works on LOCAL network (not internet)
echo.
echo 📱 Phone Access Instructions:
echo    1. Make sure your phone is on the same WiFi network as this computer
echo    2. Keep this computer ON and this server running
echo    3. Open browser on your phone
echo    4. Go to: http://%NetworkIP%:8000
echo.
echo 💻 Computer Access:
echo    Local: http://localhost:8000
echo    Network: http://%NetworkIP%:8000
echo.
echo 🔄 When server stops working:
echo    • If you close this window, phone access stops
echo    • If computer goes to sleep, phone access stops  
echo    • If you disconnect from WiFi, phone access stops
echo.
echo 🔥 Starting Django development server...
echo    Press Ctrl+C to stop the server
echo ============================================================

REM Start Django server on all interfaces
python manage.py runserver 0.0.0.0:8000

pause
