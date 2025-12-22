from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User


class Event(models.Model):
    """Model representing an event (e.g., Movie, Concert, etc.)"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    event_date = models.DateTimeField()
    location = models.CharField(max_length=200)
    total_seats = models.PositiveIntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-event_date']


class Seat(models.Model):
    """Model representing a seat in an event"""
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('reserved', 'Reserved'),
        ('locked', 'Locked'),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='seats')
    seat_number = models.CharField(max_length=10)  # e.g., "A1", "B5", etc.
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    reserved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='reserved_seats'
    )
    
    # IMPORTANT: This is the key field for preventing race conditions
    # locked_until stores when a seat's lock expires (temporary hold)
    locked_until = models.DateTimeField(null=True, blank=True)
    locked_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='locked_seats'
    )
    
    reserved_at = models.DateTimeField(null=True, blank=True)
    # When does the reservation expire? (can auto-release if not confirmed)
    reserved_until = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.event.name} - Seat {self.seat_number}"

    class Meta:
        unique_together = ('event', 'seat_number')
        ordering = ['seat_number']

    def is_locked(self):
        """Check if seat is currently locked (temporary hold)"""
        if self.locked_until is None:
            return False
        return timezone.now() < self.locked_until

    def is_available_for_selection(self):
        """Check if seat can be selected for reservation"""
        return self.status == 'available' and not self.is_locked()


class Reservation(models.Model):
    """Model representing a confirmed reservation"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='reservations')
    seats = models.ManyToManyField(Seat, related_name='reservations')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)  # When pending reservation expires

    def __str__(self):
        return f"Reservation by {self.user.username} for {self.event.name}"

    class Meta:
        ordering = ['-created_at']

    def confirm(self):
        """Confirm the pending reservation"""
        self.status = 'confirmed'
        self.expires_at = None
        for seat in self.seats.all():
            seat.status = 'reserved'
            seat.reserved_by = self.user
            seat.reserved_at = timezone.now()
            seat.locked_until = None
            seat.locked_by = None
            seat.save()
        self.save()

    def cancel(self):
        """Cancel the reservation and release seats"""
        self.status = 'cancelled'
        for seat in self.seats.all():
            seat.status = 'available'
            seat.reserved_by = None
            seat.reserved_at = None
            seat.locked_until = None
            seat.locked_by = None
            seat.save()
        self.save()
