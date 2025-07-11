#!/usr/bin/env python
"""
Script to create missing tables and fix database schema issues
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

def create_announcements_table():
    """Create announcements table if it doesn't exist"""
    try:
        with connection.cursor() as cursor:
            # Check if table exists
            cursor.execute("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME = 'announcements' 
                AND TABLE_SCHEMA = DATABASE()
            """)
            
            if cursor.fetchone()[0] == 0:
                # Create the announcements table
                cursor.execute("""
                    CREATE TABLE announcements (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        title VARCHAR(200) NOT NULL,
                        content TEXT NOT NULL,
                        announcement_type VARCHAR(20) DEFAULT 'general',
                        is_active BOOLEAN DEFAULT TRUE,
                        created_by_id INT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        start_date DATETIME,
                        end_date DATETIME,
                        FOREIGN KEY (created_by_id) REFERENCES users(id)
                    )
                """)
                print("✅ Created 'announcements' table")
            else:
                print("ℹ️ 'announcements' table already exists")
                
    except Exception as e:
        print(f"❌ Error creating announcements table: {e}")

def add_missing_room_fields():
    """Add any missing fields to rooms table"""
    try:
        with connection.cursor() as cursor:
            # Check and add building field if missing
            cursor.execute("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'rooms' 
                AND COLUMN_NAME = 'building' 
                AND TABLE_SCHEMA = DATABASE()
            """)
            
            if cursor.fetchone()[0] == 0:
                cursor.execute("ALTER TABLE rooms ADD COLUMN building VARCHAR(100) NULL")
                print("✅ Added 'building' column to rooms table")
            
            # Check and add floor field if missing
            cursor.execute("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'rooms' 
                AND COLUMN_NAME = 'floor' 
                AND TABLE_SCHEMA = DATABASE()
            """)
            
            if cursor.fetchone()[0] == 0:
                cursor.execute("ALTER TABLE rooms ADD COLUMN floor VARCHAR(10) NULL")
                print("✅ Added 'floor' column to rooms table")
                
    except Exception as e:
        print(f"❌ Error adding room fields: {e}")

if __name__ == "__main__":
    create_announcements_table()
    add_missing_room_fields()
