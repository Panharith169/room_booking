import os
import pymysql
from .settings import *

# Enable PyMySQL
pymysql.install_as_MySQLdb()

# Production settings
DEBUG = False

# Allowed hosts for PythonAnywhere
ALLOWED_HOSTS = [
    '.pythonanywhere.com',
    'localhost',
    '127.0.0.1',
]

# Database configuration for PythonAnywhere
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'panharith169$room_booking_db',  # Replace panharith169 with your username
        'USER': 'panharith169',  # Replace with your username
        'PASSWORD': 'your_database_password',  # Replace with your database password
        'HOST': 'panharith169.mysql.pythonanywhere-services.com',  # Replace panharith169 with your username
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
    }
}

# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = '/home/panharith169/room_booking/staticfiles/'  # Replace panharith169 with your username

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = '/home/panharith169/room_booking/media/'  # Replace panharith169 with your username

# Security settings
SECURE_SSL_REDIRECT = False
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
