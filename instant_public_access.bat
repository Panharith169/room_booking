@echo off
echo 🌍 Starting INSTANT PUBLIC ACCESS for Room Booking System...
echo.

REM Start Django server in background
echo 🚀 Starting Django server...
start /B python manage.py runserver 8000

REM Wait a moment for server to start
timeout /t 3 /nobreak > nul

REM Create public tunnel
echo 🌐 Creating public tunnel...
echo.
echo ✅ Your Room Booking System will be accessible worldwide!
echo 📱 Share the URL with anyone to access your app!
echo.
lt --port 8000 --subdomain rupp-room-booking

pause
