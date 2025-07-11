web: gunicorn room_booking_system.wsgi:application --bind 0.0.0.0:$PORT
release: python manage.py migrate --settings=production_settings
