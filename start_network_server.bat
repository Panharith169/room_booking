@echo off
echo Starting Django Room Booking System for Local Network...
echo.
echo Your local IP: 10.1.69.74
echo Share this URL with friends on same WiFi: http://10.1.69.74:8000
echo.
echo Press Ctrl+C to stop the server
echo.
cd /d "%~dp0"
python manage.py runserver 0.0.0.0:8000
pause
