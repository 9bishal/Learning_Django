from django.contrib import admin
from .models import Event, Seat, Reservation


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'event_date', 'location', 'total_seats')
    search_fields = ('name', 'location')
    list_filter = ('event_date',)
    ordering = ('-event_date',)


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ('seat_number', 'event', 'status', 'locked_by', 'reserved_by')
    list_filter = ('status', 'event')
    search_fields = ('seat_number', 'event__name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'event', 'status', 'total_price', 'created_at')
    list_filter = ('status', 'event', 'created_at')
    search_fields = ('user__username', 'event__name')
    readonly_fields = ('created_at', 'updated_at')

