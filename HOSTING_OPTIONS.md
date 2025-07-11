# Alternative Hosting Options for Room Booking System

## 🌐 **Option 2: Render (Easy & Free)**

### Features:
- ✅ Free tier with PostgreSQL
- ✅ Auto-deploy from GitHub
- ✅ Built-in SSL certificates
- ✅ Custom domains

### Steps:
1. **Convert to PostgreSQL** (create `settings_render.py`):
```python
import os
import dj_database_url
from .settings import *

DEBUG = False
ALLOWED_HOSTS = ['*']

# PostgreSQL Database
DATABASES = {
    'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
}

# Static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
```

2. **Create `build.sh`**:
```bash
#!/usr/bin/env bash
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
```

3. **Deploy on Render**:
   - Connect GitHub repo
   - Set build command: `./build.sh`
   - Set start command: `gunicorn room_booking_system.wsgi:application`

---

## 🌍 **Option 3: Heroku (Popular)**

### Features:
- ✅ Well-documented
- ✅ Many add-ons available
- ✅ Easy database management

### Steps:
1. **Install Heroku CLI**
2. **Create Procfile**:
```
web: gunicorn room_booking_system.wsgi:application
release: python manage.py migrate
```

3. **Deploy**:
```bash
heroku create your-app-name
heroku addons:create cleardb:ignite  # MySQL addon
git push heroku main
```

---

## 🔧 **Option 4: DigitalOcean App Platform**

### Features:
- ✅ $5/month managed database
- ✅ Easy scaling
- ✅ Professional hosting

### Steps:
1. **Create `app.yaml`**:
```yaml
name: room-booking-system
services:
- name: web
  source_dir: /
  github:
    repo: your-username/room-booking
    branch: main
  run_command: gunicorn room_booking_system.wsgi:application
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
databases:
- name: room-booking-db
  engine: MYSQL
  version: "8"
```

---

## 💻 **Option 5: VPS Hosting (Advanced)**

### Recommended VPS Providers:
- **Linode**: $5/month
- **DigitalOcean**: $6/month  
- **Vultr**: $5/month
- **AWS EC2**: $3.5/month (t2.nano)

### Setup Process:
1. **Server Setup**:
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python, Nginx, MySQL
sudo apt install python3 python3-pip nginx mysql-server -y

# Install Git
sudo apt install git -y
```

2. **Clone and Setup Project**:
```bash
git clone https://github.com/your-username/room-booking.git
cd room-booking
pip3 install -r requirements.txt
```

3. **Configure Nginx**:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /static/ {
        alias /path/to/your/project/staticfiles/;
    }
}
```

4. **Run with Gunicorn**:
```bash
gunicorn room_booking_system.wsgi:application --bind 0.0.0.0:8000
```

---

## 📊 **Hosting Comparison**

| Platform | Cost | Ease | Database | SSL | Custom Domain |
|----------|------|------|----------|-----|---------------|
| Railway | Free/$20 | ⭐⭐⭐⭐⭐ | MySQL ✅ | ✅ | ✅ |
| Render | Free/$7 | ⭐⭐⭐⭐ | PostgreSQL | ✅ | ✅ |
| Heroku | $7/month | ⭐⭐⭐⭐ | MySQL addon | ✅ | ✅ |
| DigitalOcean | $12/month | ⭐⭐⭐ | Managed DB | ✅ | ✅ |
| VPS | $5/month | ⭐⭐ | Self-managed | Manual | ✅ |

---

## 🏆 **Recommendation**

**For beginners: Railway** 
- Easy setup
- MySQL database included
- Free tier available
- Perfect for your Django + MySQL project

**For production: DigitalOcean App Platform**
- Professional hosting
- Reliable performance
- Good documentation
- Scalable
