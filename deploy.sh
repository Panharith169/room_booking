#!/bin/bash

# Deployment script for Room Booking System
# Run this script to deploy your application

echo "🚀 Starting deployment process..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install production requirements
echo "📋 Installing production requirements..."
pip install -r requirements-production.txt

# Set environment variables
echo "🔑 Setting up environment variables..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "⚠️  Please edit .env file with your production values"
    exit 1
fi

# Run migrations
echo "🗄️  Running database migrations..."
python manage.py migrate --settings=production_settings

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --settings=production_settings

# Create superuser (optional)
echo "👤 Creating superuser (optional)..."
read -p "Do you want to create a superuser? (y/n): " create_user
if [ "$create_user" = "y" ]; then
    python manage.py createsuperuser --settings=production_settings
fi

echo "✅ Deployment completed successfully!"
echo "🌐 You can now start the server with:"
echo "   gunicorn --config gunicorn.conf.py room_booking_system.wsgi:application"
