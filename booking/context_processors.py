# ===== booking/context_processors.py =====
# Create this new file

def room_types(request):
    """Add room types to template context"""
    from .models import Room
    return {
        'ROOM_TYPES': Room.ROOM_TYPES,
    }