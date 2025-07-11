#!/usr/bin/env python
"""
Django Room Booking System Startup Script
Run this script to set up and start your Django application.
"""

import os
import sys
import subprocess

def run_command(command, description):
    """Run a command and display the result"""
    print(f"\n{description}...")
    print(f"Running: {command}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        if result.stdout:
            print("Output:", result.stdout.strip())
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed")
        print("Error:", e.stderr.strip())
        return False

def main():
    print("=== Django Room Booking System Setup ===")
    print("This script will set up your Django application.")
    
    # Change to project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    print(f"Working directory: {project_dir}")
    
    # Step 1: Install requirements (if requirements.txt exists)
    if os.path.exists('requirements.txt'):
        run_command('pip install -r requirements.txt', 'Installing Python packages')
    
    # Step 2: Make migrations
    run_command('python manage.py makemigrations', 'Creating database migrations')
    
    # Step 3: Apply migrations
    run_command('python manage.py migrate', 'Applying database migrations')
    
    # Step 4: Collect static files
    run_command('python manage.py collectstatic --noinput', 'Collecting static files')
    
    # Step 5: Setup initial data
    run_command('python manage.py setup_initial_data', 'Setting up initial admin and user accounts')
    
    # Step 6: Setup rooms
    run_command('python manage.py setup_rooms', 'Setting up sample room data')
    
    print("\n=== Setup Complete ===")
    print("Your Django Room Booking System is ready!")
    print("\nDefault accounts created:")
    print("🔑 Admin: admin@rupp.edu.kh / password: admin123")
    print("👤 User: student@rupp.edu.kh / password: student123")
    
    print("\nTo start the development server, run:")
    print("python manage.py runserver")
    print("\nThen visit: http://127.0.0.1:8000")
    
    # Ask if user wants to start the server now
    start_server = input("\nWould you like to start the development server now? (y/n): ").lower()
    if start_server in ['y', 'yes']:
        print("\nStarting Django development server...")
        print("Press Ctrl+C to stop the server")
        subprocess.run('python manage.py runserver', shell=True)

if __name__ == "__main__":
    main()
