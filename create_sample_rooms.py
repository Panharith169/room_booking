#!/usr/bin/env python
"""
Script to create sample rooms for testing admin functionality
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'room_booking_system.settings')
django.setup()

def create_sample_rooms():
    """Create sample rooms for testing"""
    try:
        from booking.models import Room
        
        # Sample rooms data
        sample_rooms = [
            {
                'name': 'Conference Room A',
                'room_number': 'A-201',
                'capacity': 20,
                'room_type': 'conference',
                'description': 'Modern conference room with presentation facilities',
                'equipment': 'Projector, Whiteboard, Conference Phone',
                'is_available': True
            },
            {
                'name': 'Computer Lab 1',
                'room_number': 'A-206',
                'capacity': 30,
                'room_type': 'lab',
                'description': 'Fully equipped computer laboratory',
                'equipment': '30 PCs, Projector, Network Access',
                'is_available': True
            },
            {
                'name': 'Lecture Hall',
                'room_number': 'A-101',
                'capacity': 100,
                'room_type': 'classroom',
                'description': 'Large lecture hall for presentations',
                'equipment': 'Audio System, Projector, Microphone',
                'is_available': True
            },
            {
                'name': 'Chemistry Lab',
                'room_number': 'S-309',
                'capacity': 25,
                'room_type': 'lab',
                'description': 'Chemistry laboratory with safety equipment',
                'equipment': 'Lab Benches, Fume Hoods, Safety Equipment',
                'is_available': True
            },
            {
                'name': 'Study Room 1',
                'room_number': 'L-105',
                'capacity': 8,
                'room_type': 'study',
                'description': 'Quiet study room for small groups',
                'equipment': 'Tables, Chairs, Whiteboard',
                'is_available': True
            },
            {
                'name': 'Business Classroom',
                'room_number': 'B-301',
                'capacity': 40,
                'room_type': 'classroom',
                'description': 'Business school classroom with modern facilities',
                'equipment': 'Projector, Smart Board, Audio System',
                'is_available': True
            }
        ]
        
        created_count = 0
        for room_data in sample_rooms:
            # Check if room already exists
            if not Room.objects.filter(room_number=room_data['room_number']).exists():
                Room.objects.create(**room_data)
                created_count += 1
                print(f"✅ Created room: {room_data['name']} ({room_data['room_number']})")
            else:
                print(f"ℹ️ Room {room_data['room_number']} already exists")
        
        print(f"\n✅ Created {created_count} new rooms")
        print(f"📊 Total rooms in database: {Room.objects.count()}")
        
    except Exception as e:
        print(f"❌ Error creating sample rooms: {e}")

if __name__ == "__main__":
    create_sample_rooms()
