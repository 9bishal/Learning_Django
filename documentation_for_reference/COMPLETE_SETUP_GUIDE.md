# 🎬 Django Seat Reservation System - Complete Guide

## 🎯 Project Overview

This is a **production-ready seat reservation system** demonstrating:
- ✅ **Database-level locking** with Django's `select_for_update()`
- ✅ **Race condition prevention** for concurrent seat reservations
- ✅ **Modern React frontend** with beautiful UI/UX
- ✅ **RESTful API** with proper error handling
- ✅ **Real-time seat status** updates
- ✅ **Atomic transactions** for data integrity 

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    React Frontend (Port 3000)               │
│              Beautiful Event & Seat Selection UI             │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/CORS
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Django Backend (Port 8000)                      │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │               API Endpoints                          │  │
│  │  - /api/login/ (Authentication)                     │  │
│  │  - /api/events/ (Browse Events)                     │  │
│  │  - /api/events/<id>/seats/ (View Seats)             │  │
│  │  - /api/events/<id>/seats/<id>/lock/ ⭐ SELECT...  │  │
│  │  - /api/events/<id>/reserve/ (Confirm)              │  │
│  │  - /api/reservations/ (View Bookings)               │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Django ORM Models                       │  │
│  │  - Event (Event details)                            │  │
│  │  - Seat (Seat status + locked_until + locked_by)    │  │
│  │  - Reservation (Confirmed bookings)                 │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────┬──────────────────────────────────────────┘
                  │ SQL Queries
                  ▼
         ┌─────────────────────┐
         │  SQLite Database    │
         │  (or PostgreSQL)     │
         │  ⚡ Row-Level Locks │
         └─────────────────────┘
```

---

## 🔒 Key Concept: `select_for_update()` and `locked_until`

### The Problem: Race Conditions

```
Without locking:
Timeline:
T0: User A reads Seat#1 → status='available'
T1: User B reads Seat#1 → status='available'
T2: User A updates Seat#1 → status='reserved'
T3: User B updates Seat#1 → status='reserved' ❌ CONFLICT!
```

Both users think they successfully reserved the same seat!

### The Solution: Database-Level Locking

```python
# In views.py
with transaction.atomic():
    # select_for_update() acquires an EXCLUSIVE lock on the row
    seat = Seat.objects.select_for_update().get(id=seat_id)
    
    # No other transaction can read/write this seat until we're done
    
    if seat.status != 'available':
        return error("Seat not available")
    
    # Temporary hold for 5 minutes
    seat.locked_until = timezone.now() + timedelta(seconds=300)
    seat.save()
    
    # Lock automatically released when transaction ends
```

### Flow with Locking

```
Timeline:
T0: User A: SELECT FOR UPDATE Seat#1
    → Database acquires EXCLUSIVE LOCK
T1: User B: SELECT FOR UPDATE Seat#1
    → WAITS... lock held by User A
T2: User A updates status & locked_until
    → Transaction COMMIT, lock released
T3: User B acquires lock
    → Reads current status (locked)
    → Returns error: "Seat locked by another user"
```

### The `locked_until` Field

```python
class Seat(models.Model):
    # Status can be: 'available', 'locked', 'reserved'
    status = models.CharField(...)
    
    # ⭐ KEY FIELD: When does the temporary lock expire?
    locked_until = models.DateTimeField(null=True, blank=True)
    
    def is_locked(self):
        """Check if seat is currently locked"""
        if self.locked_until is None:
            return False
        return timezone.now() < self.locked_until
```

**How it works:**
1. User locks a seat → `locked_until = now + 5 minutes` 
2. Other users see `is_locked() = True` → can't reserve
3. If user doesn't confirm in 5 minutes → `locked_until` expires
4. Next request finds `locked_until < now` → treat as available

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 14+
- pip & npm

### Step 1: Backend Setup

```bash
cd /Users/bishalkumarshah/learning_django_basics/seat_reservation_workflow/seat_reservation

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install django django-cors-headers

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Generate sample data
python manage.py populate_events

# Start Django server
python manage.py runserver
```

**Django runs on:** `http://localhost:8000`
**Admin panel:** `http://localhost:8000/admin` (username: admin, password: admin123)

### Step 2: Frontend Setup

```bash
cd /Users/bishalkumarshah/learning_django_basics/seat_reservation_frontend

# Install dependencies
npm install

# Start React development server
npm start
```

**React runs on:** `http://localhost:3000`

---

## 📊 Database Schema Visualization

```
┌─────────────────────────────────────────────────┐
│                    Event                         │
├──────────────────────────────────────────────────┤
│ id (PK)                                         │
│ name: CharField                                 │
│ description: TextField                          │
│ event_date: DateTime                            │
│ location: CharField                             │
│ total_seats: Int                                │
│ created_at, updated_at: DateTime                │
└──────────────────────────────────────────────────┘
            │ 1
            │ │ Many
            │ └─────────────────────────────────────┐
            │                                       │
            ▼                                       ▼
┌──────────────────────────────────────────────────┐
│                     Seat                         │
├──────────────────────────────────────────────────┤
│ id (PK)                                         │
│ event_id (FK) → Event                           │
│ seat_number: Char("A1", "B5", etc.)            │
│ status: Char (available|locked|reserved)       │
│                                                 │
│ ⭐ LOCKING FIELDS:                              │
│ locked_until: DateTime (NULL = not locked)     │
│ locked_by: FK → User (who locked it)           │
│                                                 │
│ RESERVATION FIELDS:                             │
│ reserved_by: FK → User                         │
│ reserved_at: DateTime                          │
│                                                 │
│ created_at, updated_at: DateTime                │
└──────────────────────────────────────────────────┘
            │ Many
            │
            ▼ (M2M)
┌──────────────────────────────────────────────────┐
│                 Reservation                      │
├──────────────────────────────────────────────────┤
│ id (PK)                                         │
│ user_id (FK) → User                            │
│ event_id (FK) → Event                          │
│ seats (M2M) → Seat                             │
│ status: Char (pending|confirmed|cancelled)     │
│ total_price: Decimal                           │
│ created_at, updated_at: DateTime                │
│ expires_at: DateTime (if pending)               │
└──────────────────────────────────────────────────┘
```

---

## 📡 API Endpoints Reference

### Authentication

#### POST `/api/login/`
```json
Request:
{
  "username": "admin",
  "password": "admin123"
}

Response:
{
  "success": true,
  "user_id": 1,
  "username": "admin",
  "message": "Welcome, admin!"
}
```

---

### Events

#### GET `/api/events/`
```json
Response:
{
  "success": true,
  "events": [
    {
      "id": 1,
      "name": "The Matrix - Special Screening",
      "description": "A sci-fi classic...",
      "event_date": "2025-12-28T18:00:00Z",
      "location": "Central Cinema",
      "total_seats": 60,
      "available_seats": 45,
      "reserved_seats": 15
    }
  ]
}
```

---

### Seats

#### GET `/api/events/{event_id}/seats/`
```json
Response:
{
  "success": true,
  "seats": [
    {
      "id": 1,
      "seat_number": "A1",
      "status": "available",
      "is_locked": false
    },
    {
      "id": 2,
      "seat_number": "A2",
      "status": "locked",
      "is_locked": true
    },
    {
      "id": 3,
      "seat_number": "A3",
      "status": "reserved",
      "is_locked": false
    }
  ]
}
```

#### POST `/api/events/{event_id}/seats/{seat_id}/lock/` ⭐
**This is where SELECT FOR UPDATE happens!**

```json
Request: {} (no body needed)
Auth: Required

Response (Success):
{
  "success": true,
  "message": "Seat A1 locked for 5 minutes",
  "seat": {
    "id": 1,
    "seat_number": "A1",
    "locked_until": "2025-12-21T10:05:00Z",
    "status": "locked"
  }
}

Response (Error - Already locked):
{
  "success": false,
  "error": "Seat is temporarily locked by another user",
  "locked_until": "2025-12-21T10:05:00Z"
}
```

#### POST `/api/events/{event_id}/seats/{seat_id}/unlock/`
```json
Request: {}
Auth: Required

Response:
{
  "success": true,
  "message": "Seat A1 unlocked"
}
```

---

### Reservations

#### POST `/api/events/{event_id}/reserve/`
**Confirms locked seats → Makes them permanent reservations**

```json
Request:
{
  "seat_ids": [1, 3, 5]
}

Auth: Required

Response:
{
  "success": true,
  "message": "Successfully reserved 3 seat(s)",
  "reservation_id": 42,
  "seats": ["A1", "A3", "A5"]
}
```

#### GET `/api/reservations/`
```json
Response:
{
  "success": true,
  "reservations": [
    {
      "id": 42,
      "event_name": "The Matrix - Special Screening",
      "seats": ["A1", "A3", "A5"],
      "status": "confirmed",
      "total_price": "300.00",
      "created_at": "2025-12-21T10:00:00Z"
    }
  ]
}
```

#### POST `/api/reservations/{reservation_id}/cancel/`
```json
Request: {}
Auth: Required

Response:
{
  "success": true,
  "message": "Reservation cancelled"
}
```

---

## 💻 React Components

### 1. **LoginForm** (`components/LoginForm.js`)
- User authentication
- Demo credentials display
- Feature highlights

### 2. **EventList** (`components/EventList.js`)
- Browse all events
- Seat availability progress bar
- Event details (date, location)

### 3. **SeatSelector** (`components/SeatSelector.js`) ⭐ **Main Component**
- Interactive seat grid visualization
- Real-time seat status updates (polls every 3 seconds)
- Lock/unlock seats
- Selection summary with pricing
- Lock timeout information

### 4. **UserReservations** (`components/UserReservations.js`)
- View all confirmed reservations
- Cancel reservations
- Reservation details

---

## 🔍 Understanding the Complete Flow

### Scenario: Alice reserves 2 seats

```
STEP 1: Alice logs in
┌─────────────────────────────────────┐
│ POST /api/login/                    │
│ {username: "alice", password: ...}  │
│                                     │
│ → Django authenticates              │
│ → Sets session cookie               │
│ → Returns user_id                   │
└─────────────────────────────────────┘

STEP 2: Browse events
┌─────────────────────────────────────┐
│ GET /api/events/                    │
│                                     │
│ → Django queries all Event objects  │
│ → Counts available/reserved seats   │
│ → Returns event list                │
└─────────────────────────────────────┘

STEP 3: View seats for event #1
┌─────────────────────────────────────┐
│ GET /api/events/1/seats/            │
│                                     │
│ → Django queries Seat objects       │
│ → Calculates is_locked() for each   │
│ → Returns seat grid                 │
└─────────────────────────────────────┘

STEP 4: Lock seat A1 (SELECT FOR UPDATE!)
┌──────────────────────────────────────────────────┐
│ POST /api/events/1/seats/1/lock/                 │
│                                                  │
│ Django executes:                                 │
│ ├─ transaction.atomic() START                    │
│ ├─ SELECT FOR UPDATE Seat WHERE id=1             │
│ │  (DATABASE LOCKS THIS ROW)                     │
│ ├─ Verify status == 'available'? ✓              │
│ ├─ Verify is_locked() == False? ✓               │
│ ├─ Update locked_until = now + 5min              │
│ ├─ Update locked_by = alice                      │
│ ├─ Update status = 'locked'                      │
│ ├─ COMMIT (LOCK RELEASED)                       │
│ └─ Return success + locked_until timestamp       │
│                                                  │
│ → Seat A1 is now locked for Alice                │
│ → expires at 10:05:00 UTC                        │
│ → Other users see it as locked                   │
└──────────────────────────────────────────────────┘

STEP 5: Lock seat A2 (Same process)
┌──────────────────────────────────────────────────┐
│ POST /api/events/1/seats/2/lock/                 │
│                                                  │
│ → Same SELECT FOR UPDATE process                 │
│ → Alice now has 2 seats locked                   │
└──────────────────────────────────────────────────┘

STEP 6: Confirm reservation (SELECT FOR UPDATE again!)
┌──────────────────────────────────────────────────┐
│ POST /api/events/1/reserve/                      │
│ {seat_ids: [1, 2]}                              │
│                                                  │
│ Django executes:                                 │
│ ├─ transaction.atomic() START                    │
│ ├─ SELECT FOR UPDATE Seat WHERE id IN [1, 2]    │
│ │  (DATABASE LOCKS BOTH ROWS)                    │
│ ├─ Verify all locked by alice? ✓                │
│ ├─ Create Reservation(user=alice, ...)           │
│ ├─ Add seats [1, 2] to reservation               │
│ ├─ For each seat:                                │
│ │  ├─ status = 'reserved'                        │
│ │  ├─ reserved_by = alice                        │
│ │  ├─ reserved_at = now                          │
│ │  └─ Clear locked_until, locked_by              │
│ ├─ COMMIT (LOCKS RELEASED)                      │
│ └─ Return success + reservation_id               │
│                                                  │
│ → Alice's reservation confirmed!                 │
│ → Seats permanently reserved                     │
│ → Other users can't lock them                    │
└──────────────────────────────────────────────────┘

STEP 7: View reservations
┌─────────────────────────────────────┐
│ GET /api/reservations/              │
│                                     │
│ → Django queries reservations       │
│ → Prefetches related seats          │
│ → Returns Alice's bookings          │
└─────────────────────────────────────┘
```

---

## ⚠️ What Happens When Lock Expires

```
If Alice locks a seat at 10:00:00:
├─ locked_until = 10:05:00
├─ At 10:05:01, someone else tries to lock it
└─ Django checks: is_locked()
   ├─ if now (10:05:01) < locked_until (10:05:00)? NO
   ├─ → is_locked() returns False
   └─ → Treat as available!

Automatic cleanup can be done with:
```

```python
# Management command or Celery task
from django.utils import timezone
from .models import Seat

expired_locks = Seat.objects.filter(
    status='locked',
    locked_until__lt=timezone.now()
)

for seat in expired_locks:
    seat.status = 'available'
    seat.locked_until = None
    seat.locked_by = None
    seat.save()
```

---

## 🧪 Testing the Locking Mechanism

### Test 1: Basic Lock
```bash
curl -X POST http://localhost:8000/api/events/1/seats/1/lock/ \
  -H "Cookie: csrftoken=..." \
  -H "Content-Type: application/json"
```

### Test 2: Concurrent Locks (Race Condition Test)
```bash
# Terminal 1
for i in {1..5}; do
  curl -X POST http://localhost:8000/api/events/1/seats/1/lock/ &
done

# Only ONE should succeed ✓
# Others should get: "Seat is temporarily locked by another user"
```

### Test 3: Lock Timeout
```bash
# Lock a seat
curl -X POST http://localhost:8000/api/events/1/seats/1/lock/

# Wait 5 minutes + 1 second
sleep 301

# Try to lock again
curl -X POST http://localhost:8000/api/events/1/seats/1/lock/

# Should succeed now! (lock expired)
```

---

## 📝 Admin Panel Features

Visit `http://localhost:8000/admin/`:

### Event Admin
- Create/edit events
- View seat counts
- Manage event details

### Seat Admin
- Monitor all seats
- See locked/reserved status
- Track who locked/reserved each seat
- View lock expiration times

### Reservation Admin
- View all reservations
- Filter by status, event, date
- See user and seat details

---

## 🔧 Configuration

### Adjust Lock Timeout
In `views.py`:
```python
LOCK_TIMEOUT_SECONDS = 300  # Change to desired timeout
```

### Enable PostgreSQL (for production)
In `settings.py`:
```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "seat_reservation",
        "USER": "postgres",
        "PASSWORD": "your_password",
        "HOST": "localhost",
        "PORT": "5432",
    }
}
```

### CORS Settings
In `settings.py`:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://yourdomain.com",
]
```

---

## 📚 Key Concepts Summary

| Concept | Explanation |
|---------|-------------|
| `select_for_update()` | Database-level row locking preventing concurrent modifications |
| `locked_until` | Timestamp when temporary lock expires |
| `transaction.atomic()` | Ensures all DB operations succeed together or all fail |
| Atomic Transaction | All-or-nothing: either complete or rollback |
| Race Condition | When concurrent operations interfere without locking |
| Status Flow | available → locked → reserved (or back to available) |

---

## 🚀 Production Deployment

### Use PostgreSQL
SQLite has limited locking. PostgreSQL is recommended for production.

### Enable Caching
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### Use Celery for Cleanup
```python
from celery import shared_task
from django.utils import timezone
from reservations.models import Seat

@shared_task
def cleanup_expired_locks():
    """Run every 1 minute"""
    expired = Seat.objects.filter(
        status='locked',
        locked_until__lt=timezone.now()
    )
    expired.update(
        status='available',
        locked_until=None,
        locked_by=None
    )
```

### Security Headers
```python
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'corsheaders'"
```bash
pip install django-cors-headers
```

### "CORS policy: No 'Access-Control-Allow-Origin' header"
Make sure React URL is in `CORS_ALLOWED_ORIGINS` in settings.py

### Frontend can't connect to Django
- Ensure Django server is running: `python manage.py runserver`
- Check if API_BASE URL is correct in React code
- Check browser console for errors

### Seats won't lock
- Check if user is authenticated
- Verify CSRF token is being sent
- Check Django logs for errors

---

## 📖 Further Reading

- [Django ORM Locking](https://docs.djangoproject.com/en/stable/ref/models/querysets/#select-for-update)
- [Database Transactions](https://docs.djangoproject.com/en/stable/topics/db/transactions/)
- [React Hooks](https://react.dev/reference/react/hooks)
- [Axios Documentation](https://axios-http.com/docs/intro)

---

## 📞 Support

For issues or questions:
1. Check the error messages in browser console
2. Check Django server logs
3. Verify all dependencies are installed
4. Ensure Django and React are both running

---

## 📄 License

This project is for educational purposes.

---

**Happy Reserving! 🎬🎫**
