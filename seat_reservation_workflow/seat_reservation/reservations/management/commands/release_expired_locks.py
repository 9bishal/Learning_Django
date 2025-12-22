"""
Management command to release expired seat locks AND reservations
Run this periodically: python manage.py release_expired_locks
Or schedule it with Celery/APScheduler for automatic execution
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from reservations.models import Seat


class Command(BaseCommand):
    help = 'Release seat locks and reservations that have expired'

    def handle(self, *args, **options):
        now = timezone.now()
        
        # ==========================================
        # 1. RELEASE EXPIRED LOCKS (temporary holds)
        # ==========================================
        self.stdout.write(self.style.WARNING('\n🔍 Checking for expired LOCKS...'))
        
        expired_locks = Seat.objects.filter(
            status='locked',
            locked_until__isnull=False,
            locked_until__lt=now  # Lock expiration time passed
        )
        
        locks_count = expired_locks.count()
        
        if locks_count == 0:
            self.stdout.write(self.style.SUCCESS('✅ No expired locks to release'))
        else:
            for seat in expired_locks:
                old_locked_by = seat.locked_by.username if seat.locked_by else 'Unknown'
                
                # Reset seat to available
                seat.status = 'available'
                seat.locked_until = None
                seat.locked_by = None
                seat.save()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Released lock on Seat {seat.seat_number} '
                        f'(Event: {seat.event.name}, was locked by {old_locked_by})'
                    )
                )
            
            self.stdout.write(
                self.style.SUCCESS(f'\n✅ Released {locks_count} expired locks')
            )
        
        # =====================================================
        # 2. RELEASE EXPIRED RESERVATIONS (temporary holds)
        # =====================================================
        self.stdout.write(self.style.WARNING('\n🔍 Checking for expired RESERVATIONS...'))
        
        expired_reservations = Seat.objects.filter(
            status='reserved',
            reserved_until__isnull=False,
            reserved_until__lt=now  # Reservation expiration time passed
        )
        
        reservations_count = expired_reservations.count()
        
        if reservations_count == 0:
            self.stdout.write(self.style.SUCCESS('✅ No expired reservations to release'))
        else:
            for seat in expired_reservations:
                old_reserved_by = seat.reserved_by.username if seat.reserved_by else 'Unknown'
                
                # Reset seat to available
                seat.status = 'available'
                seat.reserved_by = None
                seat.reserved_at = None
                seat.reserved_until = None
                seat.save()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Expired reservation on Seat {seat.seat_number} '
                        f'(Event: {seat.event.name}, was reserved by {old_reserved_by})'
                    )
                )
            
            self.stdout.write(
                self.style.SUCCESS(f'\n✅ Released {reservations_count} expired reservations')
            )
        
        # =====================
        # 3. SUMMARY
        # =====================
        total = locks_count + reservations_count
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Total released: {total} seat locks/reservations\n'
            )
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✅ Total locks released: {count}')
        )
