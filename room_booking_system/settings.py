from pathlib import Path
import pymysql
from decouple import config

pymysql.install_as_MySQLdb()  # Enable PyMySQL as MySQL backend

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-$))$linnq%u372h2xc0_gpfp5k$aw(n(jyn!y1q4(#=+llqp&3'
DEBUG = True
ALLOWED_HOSTS = []

# Installed apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'accounts.apps.AccountsConfig',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'booking',  # your custom app

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'room_booking_system.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Use templates/ directory
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'booking.context_processors.room_types',
            ],
        },
    },
]

WSGI_APPLICATION = 'room_booking_system.wsgi.application'

# ✅ MySQL database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'room_booking',
        'USER': 'Rith',
        'PASSWORD': '123456',
        'HOST': 'localhost',
        'PORT': '3307',
        #  'OPTIONS': {
        #      'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        #      'charset': 'utf8mb4',
        #  },
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static and Media files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default PK field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ✅ Custom user model
AUTH_USER_MODEL = 'booking.CustomUser'
AUTH_USER_MODEL = 'accounts.User' 

# ✅ Auth redirect settings
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/accounts/dashboard/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

# ✅ Email backend for dev
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
