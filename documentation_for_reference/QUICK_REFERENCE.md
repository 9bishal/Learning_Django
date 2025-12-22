# 🎬 Seat Reservation System - Quick Reference

## 📂 Project Structure

```
learning_django_basics/
├── SEAT_RESERVATION_GUIDE.md              ← Comprehensive guide
├── COMPLETE_SETUP_GUIDE.md                ← Full setup instructions
├── SELECT_FOR_UPDATE_DETAILED.md          ← Deep dive into locking
│
├── seat_reservation_workflow/
│   └── seat_reservation/                  ← Django Backend
│       ├── manage.py
│       ├── reservations/                  ← Main app
│       │   ├── models.py                  ← Event, Seat, Reservation
│       │   ├── views.py                   ← API endpoints with SELECT FOR UPDATE
│       │   ├── urls.py
│       │   ├── admin.py
│       │   └── management/commands/
│       │       └── populate_events.py     ← Create sample data
│       │
│       └── seat_reservation/              ← Project settings
│           ├── settings.py
│           ├── urls.py
│           └── wsgi.py
│
└── seat_reservation_frontend/              ← React Frontend
    ├── package.json
    ├── public/
    └── src/
        ├── App.js                         ← Main app component
        ├── App.css
        └── components/
            ├── LoginForm.js               ← Authentication
            ├── EventList.js               ← Browse events
            ├── SeatSelector.js            ← Lock/reserve seats
            └── UserReservations.js        ← View bookings
```

---

## 🚀 Quick Start (Copy-Paste)

### Terminal 1: Django Backend

```bash
cd /Users/bishalkumarshah/learning_django_basics/seat_reservation_workflow/seat_reservation

# If using venv
source .venv/bin/activate

# Start server
python manage.py runserver

# Output: Starting development server at http://127.0.0.1:8000/
```

### Terminal 2: React Frontend

```bash
cd /Users/bishalkumarshah/learning_django_basics/seat_reservation_frontend

# Start React
npm start

# Browser opens: http://localhost:3000
```

### Login Credentials
- **Username:** `admin`
- **Password:** `admin123`

---

## 🔒 The Magic: `select_for_update()`

### Where It Happens

**File:** `reservations/views.py`

**Function:** `lock_seat()`

```python
@csrf_exempt
@require_http_methods(["POST"])
def lock_seat(request, event_id, seat_id):
    # ... auth checks ...
    
    with transaction.atomic():
        # ⭐ THIS LINE IS THE KEY!
        seat = Seat.objects.select_for_update().get(id=seat_id, event_id=event_id)
        
        # Database now LOCKS this row (exclusive access)
        # No other transaction can modify it
        
        # Safe to check and update
        if seat.status != 'available':
            return error()
        
        if seat.is_locked():
            return error()
        
        # Temporary hold for 5 minutes
        seat.locked_until = timezone.now() + timedelta(seconds=300)
        seat.locked_by = request.user
        seat.status = 'locked'
        seat.save()
        
        # Transaction ends, lock automatically released
        return success()
```

---

## 📊 Database Schema at a Glance

### Seat Model (The Important Fields)

```python
class Seat(models.Model):
    event = ForeignKey(Event)
    seat_number = CharField()              # "A1", "B5", etc.
    status = CharField()                   # "available", "locked", "reserved"
    
    # ⭐ LOCKING FIELDS (temporary holds)
    locked_until = DateTimeField(null=True)  # When does lock expire?
    locked_by = ForeignKey(User)             # Who locked it?
    
    # ⭐ RESERVATION FIELDS (permanent)
    reserved_by = ForeignKey(User)           # Who reserved it?
    reserved_at = DateTimeField()            # When?
```

### Status Flow

```
available
    ↓ (user clicks)
locked (temporary, expires in 5 min)
    ├─ (user confirms) → reserved (permanent)
    └─ (timeout) → available (auto)
```

---

## 🎯 API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/login/` | Authenticate user |
| GET | `/api/events/` | List all events |
| GET | `/api/events/{id}/seats/` | Get seats for event |
| POST | `/api/events/{id}/seats/{id}/lock/` | ⭐ Lock a seat (SELECT FOR UPDATE) |
| POST | `/api/events/{id}/seats/{id}/unlock/` | Release lock |
| POST | `/api/events/{id}/reserve/` | Confirm reservation |
| GET | `/api/reservations/` | View user's reservations |
| POST | `/api/reservations/{id}/cancel/` | Cancel reservation |

---

## 💻 React Components Overview

```
LoginForm
└─ User authentication
   
EventList
└─ Shows all events with availability stats
   
SeatSelector ⭐ MAIN COMPONENT
├─ Real-time seat grid (updates every 3 sec)
├─ Lock/unlock seats (calls /api/seats/{id}/lock/)
├─ Selection summary with pricing
└─ Confirm reservation (calls /api/reserve/)

UserReservations
└─ View and cancel confirmed reservations
```

---

## 🔍 Complete Request-Response Flow

### Example: Alice locks Seat A1

```
1. Frontend (React)
   ├─ POST http://localhost:8000/api/events/1/seats/1/lock/
   ├─ Headers: {X-CSRFToken: ..., Cookie: ...}
   └─ Credentials: include (for session auth)

2. Backend (Django)
   ├─ Check: is user authenticated? ✓
   ├─ Start: transaction.atomic()
   ├─ Lock: SELECT FOR UPDATE Seat#1
   │        (Database locks this row exclusively)
   │
   ├─ Verify:
   │  ├─ seat.status == 'available'? ✓
   │  └─ not seat.is_locked()? ✓
   │
   ├─ Update:
   │  ├─ seat.locked_until = now + 5min
   │  ├─ seat.locked_by = alice
   │  ├─ seat.status = 'locked'
   │  └─ seat.save()
   │
   ├─ Commit: transaction (lock released)
   │
   └─ Return:
      {
        "success": true,
        "message": "Seat A1 locked for 5 minutes",
        "seat": {
          "id": 1,
          "seat_number": "A1",
          "locked_until": "2025-12-21T10:05:00Z"
        }
      }

3. Frontend (React)
   ├─ Receive success response ✓
   ├─ Update UI: Seat A1 → Blue (selected)
   └─ Start 5-minute countdown timer
```

---

## ⚡ Why SELECT FOR UPDATE Matters

### Without It (Bug - Race Condition)
```
User A: Read Seat status = "available"
User B: Read Seat status = "available"
User A: Write Seat status = "reserved"
User B: Write Seat status = "reserved"
Result: Same seat reserved twice! 😱
```

### With It (Correct - No Race Condition)
```
User A: SELECT FOR UPDATE (lock acquired)
        Read Seat status = "available"
        Write Seat status = "reserved"
        COMMIT (lock released)

User B: SELECT FOR UPDATE (waits for lock)
        (Now acquires lock)
        Read Seat status = "reserved" (not "available"!)
        Return error: "Seat already reserved"
Result: Only one user got the seat! ✓
```

---

## 🧪 Quick Test

### Test 1: Lock a Seat
```bash
curl -X POST http://localhost:8000/api/events/1/seats/1/lock/ \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=..." \
  --data '{}'
```

### Test 2: View Seats
```bash
curl http://localhost:8000/api/events/1/seats/
```

Expected: Seat #1 shows `"status": "locked"` and `"is_locked": true`

---

## 🛠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| React won't connect to Django | Ensure Django running on port 8000 |
| CORS errors | Check CORS_ALLOWED_ORIGINS in settings.py |
| Can't lock seats | Login first, check authentication |
| Django won't start | Run `pip install django django-cors-headers` |
| React won't start | Run `npm install` |

---

## 📚 Key Files to Study

1. **Understanding the locking mechanism:**
   - `reservations/models.py` → See `Seat.is_locked()` method
   - `reservations/views.py` → See `lock_seat()` function (line ~90)

2. **Frontend calls the API:**
   - `components/SeatSelector.js` → See `handleSeatClick()` function

3. **Database setup:**
   - `reservations/models.py` → All three models (Event, Seat, Reservation)

---

## 🎓 What You're Learning

✅ Database-level row locking (SELECT FOR UPDATE)
✅ Atomic transactions (all-or-nothing)
✅ Race condition prevention
✅ Temporary hold mechanisms (locked_until field)
✅ RESTful API design
✅ React state management
✅ Frontend-backend integration
✅ Authentication & Authorization

---

## 🚀 Next Steps

1. **Experiment:** Modify LOCK_TIMEOUT_SECONDS to 60 seconds
2. **Test:** Try locking from multiple browser tabs
3. **Extend:** Add email notifications when reservation confirmed
4. **Deploy:** Push to Heroku or AWS
5. **Optimize:** Add Redis caching for seat availability

---

**Now go explore the code and see SELECT FOR UPDATE in action! 🎬🔒**
