# Railway Deployment Guide for Room Booking System

## 🚀 Railway Hosting - Step by Step

### Prerequisites
- GitHub account
- Railway account (free tier available)
- Your project pushed to GitHub

### Step 1: Prepare Your Project

1. **Create runtime.txt** (specify Python version):
```
python-3.11.0
```

2. **Update requirements.txt** (ensure all dependencies):
```
Django==4.2.7
PyMySQL==1.1.0
python-decouple==3.8
Pillow==10.1.0
gunicorn==21.2.0
whitenoise==6.6.0
```

3. **Create railway.json** (Railway configuration):
```json
{
  "deploy": {
    "startCommand": "python manage.py collectstatic --noinput && python manage.py migrate && gunicorn room_booking_system.wsgi:application",
    "healthcheckPath": "/accounts/login/"
  }
}
```

### Step 2: Production Settings

Create `settings_production.py`:
```python
from .settings import *
import os

# Production settings
DEBUG = False
ALLOWED_HOSTS = ['*']

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('MYSQL_DATABASE'),
        'USER': os.environ.get('MYSQL_USER'),
        'PASSWORD': os.environ.get('MYSQL_PASSWORD'),
        'HOST': os.environ.get('MYSQL_HOST'),
        'PORT': os.environ.get('MYSQL_PORT', '3306'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Security
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

### Step 3: Deploy to Railway

1. **Connect to Railway:**
   - Go to https://railway.app
   - Sign up with GitHub
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your room-booking repository

2. **Add MySQL Database:**
   - In Railway dashboard, click "Add Service"
   - Select "MySQL"
   - Railway will automatically create database

3. **Configure Environment Variables:**
   ```
   DJANGO_SETTINGS_MODULE=room_booking_system.settings_production
   MYSQL_DATABASE=railway (auto-generated)
   MYSQL_USER=root (auto-generated)
   MYSQL_PASSWORD=*** (auto-generated)
   MYSQL_HOST=*** (auto-generated)
   MYSQL_PORT=3306 (auto-generated)
   ```

4. **Deploy:**
   - Push your code to GitHub
   - Railway automatically deploys
   - Access via generated URL

### Step 4: Initial Setup

1. **Run migrations** (in Railway console):
```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

2. **Create admin user**:
```bash
python manage.py shell
```
```python
from accounts.models import User
from django.contrib.auth.models import Group

# Create admin user
admin = User.objects.create_user(
    email='admin@rupp.edu.kh',
    password='admin123',
    first_name='System',
    last_name='Administrator',
    is_admin=True,
    is_staff=True,
    is_superuser=True
)

# Add to admin group
admin_group, created = Group.objects.get_or_create(name='Admin')
admin.groups.add(admin_group)
```

### Step 5: Test Your Deployment

- Visit your Railway URL
- Test user registration
- Test admin login
- Test room management
- Test booking system

---

## 🌍 Live URL

Your site will be available at:
- https://your-project-name.up.railway.app

## 💰 Cost

- **Free Tier**: $5 credit monthly (enough for small projects)
- **Pro Tier**: $20/month for production use

## ✅ Benefits

- ✅ Free MySQL database included
- ✅ Automatic deployments from GitHub
- ✅ Easy environment variable management
- ✅ Built-in monitoring
- ✅ Custom domain support
- ✅ Automatic HTTPS
