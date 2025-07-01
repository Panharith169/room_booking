from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    # Room management URLs
    path('rooms/', views.room_list, name='room_list'),  # <-- Add this line for room list
    path('rooms/<int:room_id>/', views.room_detail, name='room_detail'),

    path('rooms/create/', views.room_create, name='room_create'),
    path('rooms/<int:room_id>/edit/', views.room_edit, name='room_edit'),
    path('rooms/<int:room_id>/toggle-status/', views.room_toggle_status, name='room_toggle_status'),
    path('rooms/<int:room_id>/delete/', views.room_delete, name='room_delete'),

    # Admin URLs room management
    path('admin/rooms/', views.admin_room_list, name='admin_room_list'),
    path('admin/rooms/create/', views.room_create, name='room_create'),
    path('admin/rooms/<int:room_id>/edit/', views.room_edit, name='room_edit'),
    path('admin/rooms/<int:room_id>/delete/', views.room_delete, name='room_delete'),
    path('admin/rooms/<int:room_id>/toggle-status/', views.room_toggle_status, name='room_toggle_status'),

    # AJAX endpoints
    path('api/check-availability/', views.check_room_availability, name='check_room_availability'),
]