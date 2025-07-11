from django.core.management.base import BaseCommand
from booking.models import Room, Building, BookingRule
from django.utils import timezone
from datetime import time

class Command(BaseCommand):
    help = 'Setup initial rooms, buildings, and booking rules'

    def handle(self, *args, **options):
        try:
            # Create buildings first
            buildings_data = [
                {
                    'name': 'Main Building',
                    'code': 'MAIN',
                    'address': 'RUPP Main Campus',
                    'description': 'Main academic building with lecture halls and classrooms'
                },
                {
                    'name': 'Science Building',
                    'code': 'SCI',
                    'address': 'RUPP Science Campus',
                    'description': 'Science and engineering building with labs and research facilities'
                },
                {
                    'name': 'IT Building',
                    'code': 'IT',
                    'address': 'RUPP IT Campus',
                    'description': 'Information Technology building with computer labs'
                },
                {
                    'name': 'Library Building',
                    'code': 'LIB',
                    'address': 'RUPP Library Campus',
                    'description': 'Library building with study rooms and conference rooms'
                }
            ]
            
            buildings = {}
            for building_data in buildings_data:
                try:
                    building, created = Building.objects.get_or_create(
                        name=building_data['name'],
                        defaults=building_data
                    )
                    buildings[building_data['code']] = building
                    if created:
                        self.stdout.write(
                            self.style.SUCCESS(f'Created building: {building.name}')
                        )
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f'Building model not available, skipping buildings')
                    )
                    break
            
            # Create rooms (with or without buildings)
            rooms_data = [
                # Main Building Rooms
                {
                    'name': 'Lecture Hall A',
                    'room_number': 'MAIN-A101',
                    'capacity': 100,
                    'room_type': 'auditorium',
                    'description': 'Large lecture hall with projector and sound system',
                    'equipment': 'Projector, Sound System, Microphone, Whiteboard',
                    'building': 'MAIN'
                },
                {
                    'name': 'Lecture Hall B',
                    'room_number': 'MAIN-A102',
                    'capacity': 80,
                    'room_type': 'auditorium',
                    'description': 'Medium lecture hall with modern AV equipment',
                    'equipment': 'Projector, Sound System, Whiteboard, Air Conditioning',
                    'building': 'MAIN'
                },
                {
                    'name': 'Classroom 201',
                    'room_number': 'MAIN-B201',
                    'capacity': 40,
                    'room_type': 'classroom',
                    'description': 'Standard classroom for regular classes',
                    'equipment': 'Whiteboard, Projector, Air Conditioning',
                    'building': 'MAIN'
                },
                {
                    'name': 'Classroom 202',
                    'room_number': 'MAIN-B202',
                    'capacity': 35,
                    'room_type': 'classroom',
                    'description': 'Classroom with modern furniture and equipment',
                    'equipment': 'Smart Board, Projector, Air Conditioning',
                    'building': 'MAIN'
                },
                # Science Building Rooms
                {
                    'name': 'Physics Lab',
                    'room_number': 'SCI-L101',
                    'capacity': 30,
                    'room_type': 'lab',
                    'description': 'Physics laboratory with experimental equipment',
                    'equipment': 'Lab Equipment, Workbenches, Safety Equipment, Projector',
                    'building': 'SCI'
                },
                {
                    'name': 'Chemistry Lab',
                    'room_number': 'SCI-L102',
                    'capacity': 25,
                    'room_type': 'lab',
                    'description': 'Chemistry laboratory with fume hoods and safety equipment',
                    'equipment': 'Fume Hoods, Lab Equipment, Safety Shower, Emergency Equipment',
                    'building': 'SCI'
                },
                {
                    'name': 'Biology Lab',
                    'room_number': 'SCI-L201',
                    'capacity': 28,
                    'room_type': 'lab',
                    'description': 'Biology laboratory with microscopes and specimens',
                    'equipment': 'Microscopes, Specimens, Lab Equipment, Projector',
                    'building': 'SCI'
                },
                {
                    'name': 'Engineering Workshop',
                    'room_number': 'SCI-W301',
                    'capacity': 20,
                    'room_type': 'lab',
                    'description': 'Engineering workshop with tools and machinery',
                    'equipment': 'Tools, Machinery, Safety Equipment, Workbenches',
                    'building': 'SCI'
                },
                # IT Building Rooms
                {
                    'name': 'Computer Lab 1',
                    'room_number': 'IT-C101',
                    'capacity': 30,
                    'room_type': 'lab',
                    'description': 'Computer laboratory with 30 workstations',
                    'equipment': '30 Computers, Projector, Whiteboard, Network Access',
                    'building': 'IT'
                },
                {
                    'name': 'Computer Lab 2',
                    'room_number': 'IT-C102',
                    'capacity': 25,
                    'room_type': 'lab',
                    'description': 'Computer laboratory with high-end workstations',
                    'equipment': '25 High-End Computers, Projector, Smart Board',
                    'building': 'IT'
                },
                {
                    'name': 'Server Room',
                    'room_number': 'IT-S201',
                    'capacity': 5,
                    'room_type': 'other',
                    'description': 'Server room for IT infrastructure',
                    'equipment': 'Servers, Network Equipment, Cooling System',
                    'building': 'IT'
                },
                {
                    'name': 'IT Meeting Room',
                    'room_number': 'IT-M301',
                    'capacity': 15,
                    'room_type': 'conference',
                    'description': 'Meeting room for IT department meetings',
                    'equipment': 'Conference Table, Projector, Video Conferencing',
                    'building': 'IT'
                },
                # Library Building Rooms
                {
                    'name': 'Study Room 1',
                    'room_number': 'LIB-S101',
                    'capacity': 8,
                    'room_type': 'study',
                    'description': 'Small study room for group study',
                    'equipment': 'Study Tables, Chairs, Whiteboard, Quiet Environment',
                    'building': 'LIB'
                },
                {
                    'name': 'Study Room 2',
                    'room_number': 'LIB-S102',
                    'capacity': 10,
                    'room_type': 'study',
                    'description': 'Medium study room for group projects',
                    'equipment': 'Study Tables, Chairs, Whiteboard, Power Outlets',
                    'building': 'LIB'
                },
                {
                    'name': 'Conference Room',
                    'room_number': 'LIB-C201',
                    'capacity': 20,
                    'room_type': 'conference',
                    'description': 'Conference room for meetings and presentations',
                    'equipment': 'Conference Table, Projector, Audio System, Whiteboard',
                    'building': 'LIB'
                },
                {
                    'name': 'Reading Hall',
                    'room_number': 'LIB-R301',
                    'capacity': 50,
                    'room_type': 'library',
                    'description': 'Large reading hall for silent study',
                    'equipment': 'Reading Tables, Chairs, Good Lighting, Quiet Environment',
                    'building': 'LIB'
                },
                {
                    'name': 'Library Meeting Room',
                    'room_number': 'F301',
                    'capacity': 12,
                    'room_type': 'library',
                    'description': 'Library meeting room for group discussions',
                    'equipment': 'Round Table, Chairs, Whiteboard, Quiet Zone',
                    'building': 'LIB'
                },
            ]

            created_count = 0
            for room_data in rooms_data:
                try:
                    building_code = room_data.pop('building', None)
                    if building_code and building_code in buildings:
                        room_data['building'] = buildings[building_code]
                    room, created = Room.objects.get_or_create(
                        room_number=room_data['room_number'],
                        defaults=room_data
                    )
                    if created:
                        created_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(f'Created room: {room.name} ({room.room_number})')
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(f'Room already exists: {room.room_number}')
                        )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error creating room {room_data.get("room_number", "?")}: {str(e)}')
                    )

            # Create booking rules
            try:
                rule_data = {
                    'name': 'Default Booking Rules',
                    'max_duration_hours': 4,
                    'daily_booking_limit': 3,
                    'weekly_booking_limit': 10,
                    'max_advance_days': 30,
                    'min_advance_hours': 2,
                    'min_cancel_hours': 2,
                    'min_modify_hours': 2,
                    'booking_start_time': time(7, 0),
                    'booking_end_time': time(22, 0),
                    'allow_weekends': True,
                    'is_active': True
                }
                rule, created = BookingRule.objects.get_or_create(
                    name=rule_data['name'],
                    defaults=rule_data
                )
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'Created booking rule: {rule.name}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'Booking rule already exists: {rule.name}')
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'BookingRule model not available: {str(e)}')
                )

            # Summary
            total_rooms = Room.objects.count()
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Setup completed successfully!\n'
                    f'   - Rooms: {total_rooms}'
                )
            )
        except ImportError:
            self.stdout.write(
                self.style.ERROR('Booking app not found. Skipping room creation.')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error during room setup: {str(e)}')
            )
