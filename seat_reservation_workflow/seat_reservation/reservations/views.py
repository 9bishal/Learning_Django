from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import authenticate, login as auth_login
from datetime import timedelta
import json
import logging

from .models import Event, Seat, Reservation

logger = logging.getLogger(__name__)

# LOCK TIMEOUT: How long a seat is temporarily held (in seconds)
LOCK_TIMEOUT_SECONDS = 300  # 5 minutes


@require_http_methods(["GET"])
def get_events(request):
    """
    Fetch all events with seat availability stats
    """
    try:
        events = Event.objects.all().prefetch_related('seats')
        
        events_data = []
        for event in events:
            available_count = event.seats.filter(status='available').count()
            reserved_count = event.seats.filter(status='reserved').count()
            
            events_data.append({
                'id': event.id,
                'name': event.name,
                'description': event.description,
                'event_date': event.event_date.isoformat(),
                'location': event.location,
                'total_seats': event.total_seats,
                'available_seats': available_count,
                'reserved_seats': reserved_count,
            })
        
        return JsonResponse({'success': True, 'events': events_data})
    except Exception as e:
        logger.error(f"Error fetching events: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["GET"])
def get_event_seats(request, event_id):
    """
    Fetch all seats for an event with their current status
    """
    try:
        event = get_object_or_404(Event, id=event_id)
        seats = event.seats.all()
        
        seats_data = []
        for seat in seats:
            seat_info = {
                'id': seat.id,
                'seat_number': seat.seat_number,
                'status': seat.status,
                'is_locked': seat.is_locked(),
            }
            seats_data.append(seat_info)
        
        return JsonResponse({'success': True, 'seats': seats_data})
    except Exception as e:
        logger.error(f"Error fetching event seats: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def lock_seat(request, event_id, seat_id):
    """
    LOCK A SEAT FOR TEMPORARY HOLD
    
    This uses SELECT FOR UPDATE to acquire a row-level lock on the seat
    to prevent race conditions. The lock prevents other transactions from
    modifying the seat while this transaction is in progress.
    
    Flow:
    1. User clicks on a seat to select it
    2. We acquire a lock on the seat row in the database
    3. Check if it's still available
    4. Set locked_until to current time + timeout
    5. Release the lock
    
    This ensures that even if two users try to lock the same seat
    simultaneously, only one will succeed.
    """
    try:
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'User not authenticated'}, status=401)
        
        with transaction.atomic():
            # THIS IS THE KEY: select_for_update() acquires a row-level lock
            # No other transaction can modify this row until this transaction completes
            seat = Seat.objects.select_for_update().get(id=seat_id, event_id=event_id)
            
            # Check if seat is available
            if seat.status != 'available':
                return JsonResponse({
                    'success': False, 
                    'error': f'Seat is already {seat.status}',
                    'seat_status': seat.status
                }, status=400)
            
            # Check if seat is already locked by someone else
            if seat.is_locked():
                return JsonResponse({
                    'success': False, 
                    'error': 'Seat is temporarily locked by another user',
                    'locked_until': seat.locked_until.isoformat() if seat.locked_until else None
                }, status=400)
            
            # Lock the seat for this user
            seat.locked_until = timezone.now() + timedelta(seconds=LOCK_TIMEOUT_SECONDS)
            seat.locked_by = user
            seat.status = 'locked'
            seat.save()
            
            logger.info(f"Seat {seat.seat_number} locked by user {user.username} until {seat.locked_until}")
            
            return JsonResponse({
                'success': True,
                'message': f'Seat {seat.seat_number} locked for 5 minutes',
                'seat': {
                    'id': seat.id,
                    'seat_number': seat.seat_number,
                    'locked_until': seat.locked_until.isoformat(),
                    'status': seat.status,
                }
            })
    except Seat.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Seat not found'}, status=404)
    except Exception as e:
        logger.error(f"Error locking seat: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def unlock_seat(request, event_id, seat_id):
    """
    RELEASE SEAT LOCK
    
    Used when user deselects a seat or times out
    """
    try:
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'User not authenticated'}, status=401)
        
        with transaction.atomic():
            seat = Seat.objects.select_for_update().get(id=seat_id, event_id=event_id)
            
            # Only the user who locked it can unlock it
            if seat.locked_by != user:
                return JsonResponse({
                    'success': False,
                    'error': 'You did not lock this seat'
                }, status=403)
            
            seat.locked_until = None
            seat.locked_by = None
            seat.status = 'available'
            seat.save()
            
            logger.info(f"Seat {seat.seat_number} unlocked by user {user.username}")
            
            return JsonResponse({
                'success': True,
                'message': f'Seat {seat.seat_number} unlocked'
            })
    except Seat.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Seat not found'}, status=404)
    except Exception as e:
        logger.error(f"Error unlocking seat: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def reserve_seats(request, event_id):
    """
    CONFIRM RESERVATION
    
    Convert locked seats to permanently reserved seats.
    Uses select_for_update() again to ensure atomicity.
    
    Flow:
    1. User submits seats they want to reserve
    2. We lock all those seats
    3. Check that they're all still locked by this user
    4. Create a Reservation object
    5. Mark seats as 'reserved' instead of 'locked'
    """
    try:
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'User not authenticated'}, status=401)
        
        data = json.loads(request.body)
        seat_ids = data.get('seat_ids', [])
        
        if not seat_ids:
            return JsonResponse({'success': False, 'error': 'No seats selected'}, status=400)
        
        with transaction.atomic():
            event = get_object_or_404(Event, id=event_id)
            
            # Lock all selected seats - THIS ENSURES NO RACE CONDITIONS
            # All seats are locked together atomically
            seats = list(
                Seat.objects
                .select_for_update()
                .filter(id__in=seat_ids, event=event)
            )
            
            if len(seats) != len(seat_ids):
                return JsonResponse({
                    'success': False,
                    'error': 'Some seats were not found'
                }, status=404)
            
            # Verify all seats are still locked by this user
            for seat in seats:
                if seat.status != 'locked' or seat.locked_by != user:
                    return JsonResponse({
                        'success': False,
                        'error': f'Seat {seat.seat_number} is not locked by you',
                    }, status=400)
            
            # Create reservation
            reservation = Reservation.objects.create(
                user=user,
                event=event,
                status='confirmed',
                total_price=len(seats) * 100,  # $100 per seat (example)
            )
            
            # Add seats to reservation and mark as reserved
            reservation.seats.set(seats)
            
            for seat in seats:
                seat.status = 'reserved'
                seat.reserved_by = user
                seat.reserved_at = timezone.now()
                # Set reservation expiration time (5 minutes for testing, can be changed)
                seat.reserved_until = timezone.now() + timedelta(seconds=LOCK_TIMEOUT_SECONDS)
                seat.locked_until = None
                seat.locked_by = None
                seat.save()
            
            logger.info(f"User {user.username} reserved seats: {[s.seat_number for s in seats]}")
            
            return JsonResponse({
                'success': True,
                'message': f'Successfully reserved {len(seats)} seat(s)',
                'reservation_id': reservation.id,
                'seats': [s.seat_number for s in seats],
            })
    except Exception as e:
        logger.error(f"Error reserving seats: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["GET"])
def get_user_reservations(request):
    """
    Fetch all reservations for the current user
    """
    try:
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'User not authenticated'}, status=401)
        
        reservations = Reservation.objects.filter(user=user).prefetch_related('seats', 'event')
        
        reservations_data = []
        for res in reservations:
            reservations_data.append({
                'id': res.id,
                'event_name': res.event.name,
                'seats': [s.seat_number for s in res.seats.all()],
                'status': res.status,
                'total_price': str(res.total_price),
                'created_at': res.created_at.isoformat(),
            })
        
        return JsonResponse({'success': True, 'reservations': reservations_data})
    except Exception as e:
        logger.error(f"Error fetching user reservations: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def cancel_reservation(request, reservation_id):
    """
    Cancel a reservation and release all seats
    """
    try:
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'User not authenticated'}, status=401)
        
        with transaction.atomic():
            reservation = Reservation.objects.select_related('user').get(id=reservation_id)
            
            if reservation.user != user:
                return JsonResponse({
                    'success': False,
                    'error': 'You cannot cancel someone else\'s reservation'
                }, status=403)
            
            reservation.cancel()
            
            logger.info(f"User {user.username} cancelled reservation {reservation_id}")
            
            return JsonResponse({
                'success': True,
                'message': 'Reservation cancelled'
            })
    except Reservation.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Reservation not found'}, status=404)
    except Exception as e:
        logger.error(f"Error cancelling reservation: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def login(request):
    """
    User login
    
    Accepts username and password, returns user data and token if successful
    """
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return JsonResponse({'success': False, 'error': 'Username and password required'}, status=400)
        
        from django.contrib.auth import authenticate
        
        user = authenticate(request, username=username, password=password)
        
        if user is None:
            return JsonResponse({'success': False, 'error': 'Invalid credentials'}, status=401)
        
        # If we reach here, authentication was successful
        # TODO: Generate a token for the user
        
        return JsonResponse({
            'success': True,
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'username': user.username,
                # Add other user fields as needed
            },
            # 'token': token,  # Include the token in the response
        })
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def login_user(request):
    """
    API endpoint for user login
    """
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return JsonResponse({
                'success': True,
                'user_id': user.id,
                'username': user.username,
                'message': f'Welcome, {user.username}!'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Invalid username or password'
            }, status=401)
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
