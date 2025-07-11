#!/bin/bash

# One-Click Deploy Script for RUPP Room Booking System

echo "🚀 Deploying RUPP Room Booking System..."

# Step 1: Install production dependencies
echo "📦 Installing production dependencies..."
pip install -r requirements_hosting.txt

# Step 2: Setup database
echo "🗄️ Setting up database..."
python manage.py makemigrations
python manage.py migrate

# Step 3: Create superuser (if needed)
echo "👤 Creating admin user..."
python manage.py shell -c "
from accounts.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@rupp.edu.kh', 'admin123')
    print('Admin user created: admin/admin123')
else:
    print('Admin user already exists')
"

# Step 4: Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Step 5: Start server
echo "🌐 Starting server..."
echo "Your Room Booking System is now ready!"
echo "📱 Access from any device in your network!"
echo "🔗 Local: http://localhost:8000"
echo "🔗 Network: http://$(hostname -I | awk '{print $1}'):8000"

# Start the server
python manage.py runserver 0.0.0.0:8000
