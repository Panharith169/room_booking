import os
import sys

# Add your project directory to the Python path
path = '/home/panharith169/room_booking'  # Replace panharith169 with your username
if path not in sys.path:
    sys.path.insert(0, path)

# Set the Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'room_booking_system.settings_pythonanywhere'

# Import Django's WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
