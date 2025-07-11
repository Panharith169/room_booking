@echo off
REM One-Click Deploy Script for Windows

echo 🚀 Deploying RUPP Room Booking System...

REM Step 1: Install production dependencies
echo 📦 Installing production dependencies...
pip install -r requirements_hosting.txt

REM Step 2: Setup database
echo 🗄️ Setting up database...
python manage.py makemigrations
python manage.py migrate

REM Step 3: Create superuser (if needed)
echo 👤 Creating admin user...
python manage.py shell -c "from accounts.models import User; User.objects.create_superuser('admin', 'admin@rupp.edu.kh', 'admin123') if not User.objects.filter(username='admin').exists() else print('Admin already exists')"

REM Step 4: Collect static files
echo 📁 Collecting static files...
python manage.py collectstatic --noinput

REM Step 5: Start server
echo 🌐 Starting server...
echo Your Room Booking System is now ready!
echo 📱 Access from any device in your network!
echo 🔗 Local: http://localhost:8000
echo 🔗 Network: Check your IP address

REM Start the server
python manage.py runserver 0.0.0.0:8000
