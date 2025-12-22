from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from reservations.models import Event, Seat
import string


class Command(BaseCommand):
    help = 'Generate sample events and seats for testing'

    def handle(self, *args, **options):
        self.stdout.write("Creating sample events...")
        
        # Create sample events
        event1 = Event.objects.create(
            name="The Matrix - Special Screening",
            description="A sci-fi classic. Watch the movie that changed cinema forever.",
            event_date=timezone.now() + timedelta(days=7),
            location="Central Cinema",
            total_seats=60
        )
        
        event2 = Event.objects.create(
            name="Taylor Swift - Eras Tour (Concert Film)",
            description="Experience the record-breaking concert in cinema.",
            event_date=timezone.now() + timedelta(days=14),
            location="Grand Theater",
            total_seats=100
        )
        
        event3 = Event.objects.create(
            name="Python Developers Conference 2025",
            description="Learn from industry experts about Python and Django.",
            event_date=timezone.now() + timedelta(days=30),
            location="Tech Convention Center",
            total_seats=50
        )
        
        self.stdout.write(f"Created {Event.objects.count()} events")
        
        # Generate seats for each event
        for event in [event1, event2, event3]:
            rows = ['A', 'B', 'C', 'D', 'E', 'F']
            seats_per_row = event.total_seats // len(rows)
            
            seat_count = 0
            for row in rows:
                for seat_num in range(1, seats_per_row + 1):
                    if seat_count < event.total_seats:
                        Seat.objects.create(
                            event=event,
                            seat_number=f"{row}{seat_num}",
                            status='available'
                        )
                        seat_count += 1
            
            self.stdout.write(f"Created {seat_count} seats for {event.name}")
        
        self.stdout.write(self.style.SUCCESS("Sample data created successfully!"))
        self.stdout.write("\nNow you can:")
        self.stdout.write("1. Create a superuser: python manage.py createsuperuser")
        self.stdout.write("2. Start the server: python manage.py runserver")
        self.stdout.write("3. Visit http://localhost:8000/admin to manage events")
