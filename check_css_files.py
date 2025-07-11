import os
import django
from django.conf import settings

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'room_booking_system.settings')
django.setup()

def check_css_files():
    """Check if CSS files exist and are accessible"""
    
    css_files = [
        'AdminPage/css/admin_room_form.css',
        'AdminPage/css/allBookings.css',
        'AdminPage/css/viewRooms.css',
        'AdminPage/css/adminHomePage.css'
    ]
    
    print("=== CSS Files Check ===")
    print(f"Static Root: {settings.STATIC_ROOT}")
    print(f"Static URL: {settings.STATIC_URL}")
    print()
    
    for css_file in css_files:
        static_path = os.path.join(settings.STATIC_ROOT, css_file)
        original_path = os.path.join(settings.BASE_DIR, 'static', css_file)
        
        print(f"CSS File: {css_file}")
        print(f"  Static Path: {static_path}")
        print(f"  Exists in static: {os.path.exists(static_path)}")
        print(f"  Original Path: {original_path}")
        print(f"  Exists in source: {os.path.exists(original_path)}")
        
        if os.path.exists(static_path):
            file_size = os.path.getsize(static_path)
            print(f"  File size: {file_size} bytes")
        print()

if __name__ == "__main__":
    check_css_files()
