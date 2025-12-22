# 🔓 Auto-Releasing Expired Seat Locks

## 🎯 The Problem

When a user locks a seat, it's locked for 5 minutes:
```python
seat.locked_until = timezone.now() + timedelta(seconds=300)
```

But if the user **never confirms the reservation**, the lock stays in the database forever. ❌

### Current Behavior (BUG)
```
T=0s:    User locks Seat A1
         → locked_until = 10:05:00
         
T=305s:  Lock has expired (5+ min passed)
         → locked_until < now
         
T=306s:  But Seat A1 is STILL locked! ❌ 
         No one can reserve it
         
T=1000s: Still locked! Still locked! Still locked! 😱
```

### Expected Behavior (FIXED)
```
T=0s:    User locks Seat A1
         → locked_until = 10:05:00
         
T=305s:  Lock has expired (5+ min passed)
         → locked_until < now
         
T=306s:  ✅ AUTOMATICALLY released!
         Seat A1 back to "available"
         Other users can now reserve it
```

---

## 🛠️ Solution 1: Manual Command (For Testing)

### Use This to Test Now

```bash
cd /Users/bishalkumarshah/learning_django_basics/seat_reservation_workflow/seat_reservation

# Create the management command (already done)
# File: reservations/management/commands/release_expired_locks.py

# Run it manually whenever you want
python manage.py release_expired_locks
```

### Output Example
```
✅ Released lock on Seat A1 (Event: Concert XYZ, was locked by alice)
✅ Released lock on Seat B3 (Event: Taylor Swift, was locked by bob)
✅ Released lock on Seat C5 (Event: Python Conf, was locked by charlie)

✅ Total locks released: 3
```

---

## 🚀 Solution 2: Automatic Background Task (Production)

### Option A: Using Django APScheduler (Recommended for Beginners)

This runs a task automatically every minute.

#### Step 1: Install APScheduler

```bash
pip install django-apscheduler
```

#### Step 2: Create a Task File

Create `reservations/tasks.py`:

```python
"""
Periodic tasks for seat reservation system
These run automatically in the background
"""

from django.utils import timezone
from django.db.models import Q
from reservations.models import Seat


def release_expired_locks():
    """
    Background task that runs periodically
    Releases all seat locks that have expired
    """
    now = timezone.now()
    
    # Find expired locks
    expired_locks = Seat.objects.filter(
        status='locked',
        locked_until__isnull=False,
        locked_until__lt=now
    )
    
    count = 0
    for seat in expired_locks:
        seat.status = 'available'
        seat.locked_until = None
        seat.locked_by = None
        seat.save()
        count += 1
        
        print(f'🔓 Released: Seat {seat.seat_number} (Event: {seat.event.name})')
    
    if count > 0:
        print(f'✅ Auto-released {count} expired locks')
    
    return count
```

#### Step 3: Register the Task in Settings

In `seat_reservation/settings.py`, add:

```python
# ... existing code ...

INSTALLED_APPS = [
    # ... existing apps ...
    'django_apscheduler',
    'reservations',
]

# APScheduler Configuration
APSCHEDULER_DATETIME_FORMAT = "N j, Y, f:s a"

SCHEDULER_CONFIG = {
    "apscheduler.jobstores.default": {
        "class": "apscheduler.jobstores.memory:MemoryJobStore"
    },
    "apscheduler.executors.default": {
        "class": "apscheduler.executors.threading:ThreadPoolExecutor",
        "max_workers": "10"
    },
    "apscheduler.job_defaults.coalesce": "false",
    "apscheduler.job_defaults.max_instances": "1",
    "apscheduler.timezone": "UTC",
}

SCHEDULER_JOBS = [
    {
        'id': 'release_expired_locks',
        'func': 'reservations.tasks.release_expired_locks',
        'trigger': 'interval',
        'seconds': 60,  # Run every 60 seconds
    }
]
```

#### Step 4: Create an App Ready Signal

Create `reservations/apps.py`:

```python
from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class ReservationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reservations'

    def ready(self):
        """
        Initialize APScheduler when Django app starts
        """
        try:
            from django_apscheduler.apps import DjangoApschedulerConfig
            from apscheduler.schedulers.background import BackgroundScheduler
            from reservations.tasks import release_expired_locks
            
            scheduler = BackgroundScheduler()
            
            # Add the periodic task
            scheduler.add_job(
                release_expired_locks,
                trigger='interval',
                seconds=60,  # Run every 60 seconds
                id='release_expired_locks',
                name='Release expired seat locks',
                replace_existing=True
            )
            
            if not scheduler.running:
                scheduler.start()
                logger.info("✅ Scheduler started: Expired locks will be released every 60 seconds")
            
        except Exception as e:
            logger.error(f"❌ Failed to start scheduler: {e}")
```

#### Step 5: Start Django Server

```bash
python manage.py runserver
```

**Output in terminal:**
```
✅ Scheduler started: Expired locks will be released every 60 seconds
Starting development server at http://127.0.0.1:8000/

🔓 Released: Seat A1 (Event: Concert XYZ)
🔓 Released: Seat B3 (Event: Taylor Swift)
✅ Auto-released 2 expired locks
```

---

### Option B: Using Celery (Advanced)

For larger apps with heavy background tasks:

```bash
pip install celery redis
```

**celery_tasks.py:**
```python
from celery import shared_task
from django.utils import timezone
from reservations.models import Seat


@shared_task
def release_expired_locks():
    """Celery task to release expired locks"""
    now = timezone.now()
    expired = Seat.objects.filter(
        status='locked',
        locked_until__lt=now
    )
    
    count = expired.update(
        status='available',
        locked_until=None,
        locked_by=None
    )
    
    return f'Released {count} locks'
```

---

## 📊 Comparison of Solutions

| Solution | Setup Time | Auto? | Accuracy | Best For |
|----------|-----------|-------|----------|----------|
| **Manual Command** | 5 min | ❌ NO | Perfect | Testing, debugging |
| **APScheduler** | 15 min | ✅ YES (every 60s) | Good | Small projects |
| **Celery** | 30 min | ✅ YES | Perfect | Large projects, many tasks |
| **Cron Job** | 5 min | ✅ YES | Good | Linux servers only |

---

## 🔧 Testing the Auto-Release

### Quick Test with Manual Command

```bash
# Terminal 1: Start Django server
cd seat_reservation_workflow/seat_reservation
python manage.py runserver

# Terminal 2: Lock a seat (via React or curl)
curl -X POST http://localhost:8000/api/events/1/seats/1/lock/ \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=..." \
  --data '{}'

# Check database - seat is locked
curl http://localhost:8000/api/events/1/seats/

# Wait 5+ minutes...

# Terminal 3: Release expired locks manually
cd seat_reservation_workflow/seat_reservation
python manage.py release_expired_locks

# Output:
# ✅ Released lock on Seat A1 (Event: Concert XYZ, was locked by admin)
# ✅ Total locks released: 1

# Check database again - seat is now available!
curl http://localhost:8000/api/events/1/seats/
```

### Test with APScheduler (Auto Every 60 Seconds)

```bash
# Terminal 1: Start Django (scheduler starts automatically)
python manage.py runserver

# You'll see:
# ✅ Scheduler started: Expired locks will be released every 60 seconds

# Terminal 2: Lock a seat
curl -X POST http://localhost:8000/api/events/1/seats/1/lock/ \
  -H "Content-Type: application/json" \
  --data '{}'

# Wait 5 minutes...

# Terminal 1 will show (automatically):
# 🔓 Released: Seat A1 (Event: Concert XYZ)
# ✅ Auto-released 1 expired locks

# Seat is now automatically available!
```

---

## 🐛 Debugging: Why Locks Aren't Being Released

### Check 1: Is the lock actually expired?

```python
# In Django shell
python manage.py shell

from reservations.models import Seat
from django.utils import timezone

seat = Seat.objects.get(id=1)
print(f"Seat status: {seat.status}")
print(f"Locked until: {seat.locked_until}")
print(f"Current time: {timezone.now()}")
print(f"Is expired?: {seat.locked_until < timezone.now()}")
```

### Check 2: Run the command manually

```bash
python manage.py release_expired_locks

# If nothing happens, check:
# - Are there any locked seats?
# - Have they been locked for 5+ minutes?
```

### Check 3: Verify scheduler is running (APScheduler)

```bash
# Look for this in terminal output when Django starts:
# ✅ Scheduler started: Expired locks will be released every 60 seconds

# If not showing, check settings.py
```

---

## 📝 Add to Your Models (Optional Enhancement)

You can also add a helper method to the Seat model:

```python
# In reservations/models.py

class Seat(models.Model):
    # ... existing fields ...
    
    def release_lock_if_expired(self):
        """
        Check if this seat's lock has expired.
        If yes, release it and return True.
        """
        if self.status == 'locked' and self.locked_until:
            if self.locked_until < timezone.now():
                self.status = 'available'
                self.locked_until = None
                self.locked_by = None
                self.save()
                return True
        return False
    
    @staticmethod
    def release_all_expired_locks():
        """
        Release all expired locks in the system
        """
        now = timezone.now()
        expired = Seat.objects.filter(
            status='locked',
            locked_until__isnull=False,
            locked_until__lt=now
        )
        count = expired.update(
            status='available',
            locked_until=None,
            locked_by=None
        )
        return count
```

Then in your views, you could call:

```python
# Before showing seats to user, refresh expired locks
Seat.release_all_expired_locks()

# Get seats
seats = Seat.objects.filter(event_id=event_id)
```

---

## 🎯 Recommended: Quick Setup for Your Project

### For NOW (Immediate Fix - 5 minutes):

Use the **manual command** to test:

```bash
cd /Users/bishalkumarshah/learning_django_basics/seat_reservation_workflow/seat_reservation
python manage.py release_expired_locks
```

### For LATER (Production - 15 minutes):

Use **APScheduler** for automatic release every 60 seconds.

### For LATER (Large Scale):

Use **Celery** with Redis for distributed task queue.

---

## 📊 Visualization: How Auto-Release Works

```
Timeline with APScheduler (60-second interval):

T=0s:    User locks Seat A1
         └─ locked_until = 10:05:00

T=60s:   Scheduler runs
         └─ Check: Any expired locks?
         └─ Nope, A1 not expired yet
         └─ Continue

T=120s:  Scheduler runs
         └─ Check: Any expired locks?
         └─ Nope, A1 not expired yet
         └─ Continue

T=180s:  Scheduler runs
         └─ Check: Any expired locks?
         └─ Nope, A1 not expired yet
         └─ Continue

T=240s:  Scheduler runs
         └─ Check: Any expired locks?
         └─ Nope, A1 not expired yet
         └─ Continue

T=300s:  Scheduler runs
         └─ Check: Any expired locks?
         └─ YES! A1.locked_until (10:05:00) < now (10:05:00) ✓
         └─ Release A1: status = 'available'
         └─ 🔓 Released Seat A1

T=301s:  User tries to lock A1
         └─ A1 is now available! ✓
         └─ Lock successful!
```

---

## 🎬 Summary

**The Problem:** Locks don't auto-expire

**The Solution:** Add a background task that runs every 60 seconds

**Quick Fix:** Run `python manage.py release_expired_locks` manually

**Auto Fix:** Use APScheduler or Celery

**Best Practice:** Combine with database triggers for maximum reliability

---

Now expired locks will be automatically released! 🎉🔓
