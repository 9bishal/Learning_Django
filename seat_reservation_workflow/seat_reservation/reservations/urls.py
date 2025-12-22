from django.urls import path
from . import views

app_name = 'reservations'

urlpatterns = [
    # Authentication
    path('api/login/', views.login_user, name='login'),
    
    # Event endpoints
    path('api/events/', views.get_events, name='get_events'),
    path('api/events/<int:event_id>/seats/', views.get_event_seats, name='get_event_seats'),
    
    # Seat locking endpoints - THIS IS WHERE select_for_update() HAPPENS
    path('api/events/<int:event_id>/seats/<int:seat_id>/lock/', views.lock_seat, name='lock_seat'),
    path('api/events/<int:event_id>/seats/<int:seat_id>/unlock/', views.unlock_seat, name='unlock_seat'),
    
    # Reservation endpoints
    path('api/events/<int:event_id>/reserve/', views.reserve_seats, name='reserve_seats'),
    path('api/reservations/', views.get_user_reservations, name='get_user_reservations'),
    path('api/reservations/<int:reservation_id>/cancel/', views.cancel_reservation, name='cancel_reservation'),
]
