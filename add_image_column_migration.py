#!/usr/bin/env python
"""
Script to add the missing image column to the rooms table
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'room_booking_system.settings')
django.setup()

from django.db import connection

def add_image_column():
    """Add image column to rooms table"""
    try:
        with connection.cursor() as cursor:
            # Check if column already exists
            cursor.execute("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'rooms' 
                AND COLUMN_NAME = 'image' 
                AND TABLE_SCHEMA = DATABASE()
            """)
            
            if cursor.fetchone()[0] == 0:
                # Add the image column
                cursor.execute("""
                    ALTER TABLE rooms 
                    ADD COLUMN image VARCHAR(100) NULL
                """)
                print("✅ Added 'image' column to rooms table")
            else:
                print("ℹ️ 'image' column already exists in rooms table")
                
    except Exception as e:
        print(f"❌ Error adding image column: {e}")

if __name__ == "__main__":
    add_image_column()
