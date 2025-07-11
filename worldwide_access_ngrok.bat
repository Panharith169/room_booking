@echo off
echo 🌍 Setting up WORLDWIDE ACCESS for your Room Booking System...
echo.
echo This will allow ANYONE with different WiFi to access your app!
echo.

REM Step 1: Check if ngrok is installed
where ngrok >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Ngrok not found! Please download it first:
    echo.
    echo 1. Go to: https://ngrok.com
    echo 2. Sign up for FREE account
    echo 3. Download ngrok.exe
    echo 4. Put ngrok.exe in this folder: %cd%
    echo 5. Run this script again
    echo.
    pause
    exit /b
)

echo ✅ Ngrok found! Starting worldwide tunnel...
echo.

REM Step 2: Start Django server
echo 🚀 Starting Django server...
start /B python manage.py runserver 8000

REM Wait for server to start
timeout /t 5 /nobreak > nul

REM Step 3: Create public tunnel
echo 🌐 Creating worldwide tunnel...
echo.
echo 🎉 Your Room Booking System will be accessible from ANY WiFi network!
echo 📱 Share the https URL with anyone around the world!
echo.
ngrok http 8000

pause
