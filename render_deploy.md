# Deploy to Render (FREE & RELIABLE)

## Step 1: Create render.yaml
```yaml
services:
  - type: web
    name: room-booking-system
    env: python
    buildCommand: pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
    startCommand: gunicorn room_booking_system.wsgi:application
    envVars:
      - key: DEBUG
        value: False
      - key: ALLOWED_HOSTS
        value: .onrender.com
      - key: DATABASE_URL
        fromDatabase:
          name: room-booking-db
          property: connectionString

databases:
  - name: room-booking-db
    databaseName: room_booking
    user: room_booking_user
```

## Step 2: Deploy
1. Go to https://render.com
2. Connect your GitHub account
3. Select your repository
4. Render will auto-deploy

## Your app will be live at: https://your-app-name.onrender.com

## Benefits:
✅ FREE hosting (with some limitations)
✅ Automatic HTTPS
✅ Free PostgreSQL database
✅ Auto-deploys from Git
