# Deployment Guide for RUPP Room Booking System

## 📋 Hosting Options

### 1. Cloud Platforms (Recommended)

#### **Heroku** (Beginner-friendly)
```bash
# Install Heroku CLI
# Create Heroku app
heroku create your-app-name

# Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DEBUG=False
heroku config:set DJANGO_SETTINGS_MODULE=production_settings

# Add PostgreSQL addon
heroku addons:create heroku-postgresql:hobby-dev

# Deploy
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

#### **Railway** (Modern alternative)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

#### **DigitalOcean App Platform**
1. Connect your GitHub repository
2. Set environment variables in the dashboard
3. Deploy automatically

### 2. VPS/Server Deployment

#### **Prerequisites**
- Ubuntu 20.04+ server
- Domain name (optional)
- SSL certificate (Let's Encrypt recommended)

#### **Installation Steps**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3 python3-pip python3-venv nginx postgresql postgresql-contrib

# Clone your repository
git clone https://github.com/yourusername/room-booking-system.git
cd room-booking-system

# Run deployment script
chmod +x deploy.sh
./deploy.sh

# Configure Nginx
sudo cp nginx.conf /etc/nginx/sites-available/room-booking
sudo ln -s /etc/nginx/sites-available/room-booking /etc/nginx/sites-enabled/
sudo systemctl restart nginx

# Create systemd service
sudo cp room-booking.service /etc/systemd/system/
sudo systemctl enable room-booking
sudo systemctl start room-booking
```

### 3. Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate --settings=production_settings

# Create superuser
docker-compose exec web python manage.py createsuperuser --settings=production_settings
```

## 🔧 Environment Configuration

### Required Environment Variables
```env
SECRET_KEY=your-super-secret-key
DEBUG=False
DB_NAME=room_booking_prod
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
EMAIL_HOST_USER=your-email@domain.com
EMAIL_HOST_PASSWORD=your-app-password
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

## 🗄️ Database Setup

### PostgreSQL (Recommended for production)
```bash
# Create database and user
sudo -u postgres psql
CREATE DATABASE room_booking_prod;
CREATE USER booking_admin WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE room_booking_prod TO booking_admin;
\q
```

### MySQL (Current setup)
- Update your current MySQL configuration
- Ensure MySQL server is running
- Backup your existing data

## 🔒 Security Checklist

- [ ] Change SECRET_KEY for production
- [ ] Set DEBUG=False
- [ ] Configure ALLOWED_HOSTS
- [ ] Set up HTTPS/SSL
- [ ] Configure firewall
- [ ] Set up database backups
- [ ] Configure monitoring

## 📊 Monitoring & Maintenance

### Log Monitoring
```bash
# View application logs
tail -f django.log

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Database Backups
```bash
# PostgreSQL backup
pg_dump room_booking_prod > backup_$(date +%Y%m%d).sql

# MySQL backup
mysqldump -u username -p room_booking > backup_$(date +%Y%m%d).sql
```

## 🚀 Quick Start Commands

### Local Development
```bash
python manage.py runserver
```

### Production
```bash
gunicorn --config gunicorn.conf.py room_booking_system.wsgi:application
```

### With Docker
```bash
docker-compose up -d
```

## 📞 Support

For deployment issues:
1. Check logs: `tail -f django.log`
2. Verify environment variables
3. Test database connection
4. Check static files configuration

## 🌐 Domain & SSL

### Cloudflare (Recommended)
1. Add your domain to Cloudflare
2. Enable SSL/TLS
3. Set up page rules for caching

### Let's Encrypt SSL
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

## 📈 Performance Optimization

- Enable static file caching
- Use CDN for media files
- Configure database indexing
- Set up Redis for caching
- Enable Gzip compression
