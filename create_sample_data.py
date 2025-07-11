#!/usr/bin/env python
"""
Setup script to create initial data for the Room Booking System
"""
import os
import sys
import django

# Add the project directory to the path
sys.path.append(r'C:\Users\User\Desktop\Year2\Project_S2\RoomBooking')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'room_booking_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from booking.models import Room, BookingRule
from accounts.views import assign_user_role

User = get_user_model()

def create_sample_data():
    """Create sample data for testing"""
    print("Creating sample data for Room Booking System...")
    
    # Create groups
    print("1. Creating user groups...")
    admin_group, created = Group.objects.get_or_create(name='Admin')
    user_group, created = Group.objects.get_or_create(name='User')
    print("   ✓ Groups created")
    
    # Create admin user
    print("2. Creating admin user...")
    admin_email = "admin@rupp.edu.kh"
    if not User.objects.filter(email=admin_email).exists():
        admin_user = User.objects.create_user(
            email=admin_email,
            password="admin123",
            first_name="Admin",
            last_name="User",
            student_id="ADM001",
            phone_number="012-345-678",
            faculty="Administration",
            department="IT Department"
        )
        assign_user_role(admin_user, 'Admin')
        print(f"   ✓ Admin user created: {admin_email} / admin123")
    else:
        print(f"   ✓ Admin user already exists: {admin_email}")
    
    # Create sample student users
    print("3. Creating sample student users...")
    students = [
        {
            "email": "student1@rupp.edu.kh",
            "password": "student123",
            "first_name": "Sopheak",
            "last_name": "Chan",
            "student_id": "STU001",
            "faculty": "Science",
            "department": "Computer Science"
        },
        {
            "email": "student2@rupp.edu.kh", 
            "password": "student123",
            "first_name": "Sokha",
            "last_name": "Pich",
            "student_id": "STU002",
            "faculty": "Engineering",
            "department": "Civil Engineering"
        },
        {
            "email": "student3@rupp.edu.kh",
            "password": "student123", 
            "first_name": "Sreypov",
            "last_name": "Leng",
            "student_id": "STU003",
            "faculty": "Business",
            "department": "Business Administration"
        }
    ]
    
    for student_data in students:
        if not User.objects.filter(email=student_data["email"]).exists():
            student = User.objects.create_user(
                email=student_data["email"],
                password=student_data["password"],
                first_name=student_data["first_name"],
                last_name=student_data["last_name"],
                student_id=student_data["student_id"],
                phone_number="012-345-678",
                faculty=student_data["faculty"],
                department=student_data["department"]
            )
            assign_user_role(student, 'User')
            print(f"   ✓ Student created: {student_data['email']} / {student_data['password']}")
        else:
            print(f"   ✓ Student already exists: {student_data['email']}")
    
    # Create sample rooms
    print("4. Creating sample rooms...")
    sample_rooms = [
        {
            "name": "Computer Lab 1",
            "room_number": "A-101",
            "capacity": 30,
            "room_type": "lab",
            "description": "Fully equipped computer laboratory with 30 workstations",
            "equipment": "30 PCs, Projector, Whiteboard, Air Conditioning"
        },
        {
            "name": "Lecture Hall A",
            "room_number": "A-201",
            "capacity": 100,
            "room_type": "classroom", 
            "description": "Large lecture hall for presentations and seminars",
            "equipment": "Projector, Audio System, Microphones, Whiteboard"
        },
        {
            "name": "Conference Room",
            "room_number": "A-301",
            "capacity": 20,
            "room_type": "conference",
            "description": "Professional conference room for meetings",
            "equipment": "Conference Table, Projector, Video Conferencing, Whiteboard"
        },
        {
            "name": "Science Lab",
            "room_number": "S-205",
            "capacity": 25,
            "room_type": "lab",
            "description": "Science laboratory for experiments and research",
            "equipment": "Lab Equipment, Safety Gear, Ventilation System, Emergency Shower"
        },
        {
            "name": "Study Room 1",
            "room_number": "L-105",
            "capacity": 8,
            "room_type": "study",
            "description": "Quiet study room for group work",
            "equipment": "Study Tables, Chairs, Whiteboard, Good Lighting"
        },
        {
            "name": "Business Classroom",
            "room_number": "B-301",
            "capacity": 40,
            "room_type": "classroom",
            "description": "Modern classroom for business courses",
            "equipment": "Smart Board, Projector, Student Desks, Air Conditioning"
        },
        {
            "name": "Chemistry Lab",
            "room_number": "S-309",
            "capacity": 25,
            "room_type": "lab",
            "description": "Specialized chemistry laboratory",
            "equipment": "Chemical Hoods, Lab Benches, Safety Equipment, Emergency Systems"
        },
        {
            "name": "Seminar Room",
            "room_number": "A-401",
            "capacity": 15,
            "room_type": "conference",
            "description": "Small seminar room for discussions",
            "equipment": "Round Table, Chairs, TV Display, WiFi"
        }
    ]
    
    for room_data in sample_rooms:
        if not Room.objects.filter(room_number=room_data["room_number"]).exists():
            room = Room.objects.create(**room_data)
            print(f"   ✓ Room created: {room_data['name']} ({room_data['room_number']})")
        else:
            print(f"   ✓ Room already exists: {room_data['room_number']}")
    
    # Create booking rules
    print("5. Creating booking rules...")
    if not BookingRule.objects.filter(name="Default Rules").exists():
        booking_rule = BookingRule.objects.create(
            name="Default Rules",
            max_duration_hours=8,
            daily_booking_limit=3,
            weekly_booking_limit=10,
            max_advance_days=30,
            min_advance_hours=2,
            min_cancel_hours=2,
            min_modify_hours=2,
            is_active=True
        )
        print("   ✓ Default booking rules created")
    else:
        print("   ✓ Booking rules already exist")
    
    print("\n" + "="*50)
    print("SAMPLE DATA CREATION COMPLETE!")
    print("="*50)
    print("Admin Login:")
    print("  Email: admin@rupp.edu.kh")
    print("  Password: admin123")
    print()
    print("Student Logins:")
    print("  Email: student1@rupp.edu.kh / Password: student123")
    print("  Email: student2@rupp.edu.kh / Password: student123") 
    print("  Email: student3@rupp.edu.kh / Password: student123")
    print()
    print(f"Total Rooms Created: {Room.objects.count()}")
    print(f"Total Users Created: {User.objects.count()}")
    print()
    print("You can now test the system at: http://127.0.0.1:8000/")
    print("="*50)

if __name__ == "__main__":
    try:
        create_sample_data()
    except Exception as e:
        print(f"Error creating sample data: {e}")
        import traceback
        traceback.print_exc()
