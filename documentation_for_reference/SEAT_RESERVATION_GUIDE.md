# Seat Reservation System - Complete Guide

## 📚 Overview

This is a comprehensive Django seat reservation system with **proper database locking** using Django's `select_for_update()` method. This prevents race conditions where two users might reserve the same seat simultaneously.

---

## 🗂️ Database Schema

### Models Overview

#### 1. **Event Model**
```python
Event
├── name: CharField (Event name)
├── description: TextField
├── event_date: DateTimeField
├── location: CharField
├── total_seats: PositiveIntegerField
├── created_at: DateTimeField (auto)
├── updated_at: DateTimeField (auto)
└── relationships:
    └── seats: ForeignKey (reverse relation)
    └── reservations: ForeignKey (reverse relation)
```

**Purpose**: Represents an event (movie, concert, conference, etc.)

**Example**:
```
Event: "The Matrix - Special Screening"
- Date: 2025-12-28
- Location: Central Cinema
- Total Seats: 60
```

---

#### 2. **Seat Model** ⭐ KEY MODEL
```python
Seat
├── event: ForeignKey → Event
├── seat_number: CharField (e.g., "A1", "B5")
├── status: CharField (choices: 'available', 'reserved', 'locked')
│
├── LOCKING FIELDS (for temporary holds):
├── locked_until: DateTimeField ← KEY FIELD FOR PREVENTING RACE CONDITIONS
├── locked_by: ForeignKey → User (who locked it)
│
├── RESERVATION FIELDS (for confirmed reservations):
├── reserved_by: ForeignKey → User (who permanently reserved it)
├── reserved_at: DateTimeField
│
└── Metadata:
    ├── created_at: DateTimeField
    └── updated_at: DateTimeField
```

**Key Concept - The `locked_until` Field**:
- When a user selects a seat, we set `locked_until = now() + 5 minutes`
- This creates a **temporary hold** on the seat
- If `locked_until` hasn't expired yet, other users cannot lock/reserve it
- When timeout expires, the seat automatically becomes available again

**Status Flow**:
```
available → locked (user selecting) → reserved (confirmed)
  ↑                                         ↓
  └─── cancelled (reverted to available)
```

---

#### 3. **Reservation Model**
```python
Reservation
├── user: ForeignKey → User
├── event: ForeignKey → Event
├── seats: ManyToManyField → Seat
├── status: CharField (choices: 'pending', 'confirmed', 'cancelled')
├── total_price: DecimalField
├── created_at: DateTimeField
├── updated_at: DateTimeField
└── expires_at: DateTimeField (when pending reservation expires)
```

**Purpose**: Stores confirmed seat reservations

---

## 🔒 How `select_for_update()` Prevents Race Conditions

### The Problem (Race Condition)

Without locking, this could happen:

```
Timeline:
T1: User A reads Seat#1 status: "available"
T2: User B reads Seat#1 status: "available"
T3: User A locks Seat#1 (success)
T4: User B locks Seat#1 (success) ❌ PROBLEM! Two users locked same seat
```

### The Solution (Database-Level Locking)

With `select_for_update()`:

```
Timeline:
T1: User A: Seat.objects.select_for_update().get(id=1)
    → Database acquires EXCLUSIVE LOCK on Seat#1 row
    → No other transaction can read/write this row
T2: User B: Seat.objects.select_for_update().get(id=1)
    → Waits... waiting for lock to be released
T3: User A's transaction completes → lock released
T4: User B acquires lock → reads Seat#1 status
```

### Code Example

```python
# In views.py - lock_seat function

with transaction.atomic():
    # THIS LINE ACQUIRES A DATABASE-LEVEL LOCK
    seat = Seat.objects.select_for_update().get(id=seat_id, event_id=event_id)
    
    # Only this transaction can execute code below
    # No other transaction can modify this seat row
    
    if seat.status != 'available':
        return error("Seat not available")
    
    # Check if already locked by someone else
    if seat.is_locked():
        return error("Seat locked by another user")
    
    # Lock it for 5 minutes
    seat.locked_until = timezone.now() + timedelta(seconds=300)
    seat.locked_by = user
    seat.status = 'locked'
    seat.save()
    
    # When transaction ends, lock is automatically released
```

---

## 📡 API Endpoints

### 1. Get All Events
```
GET /api/events/

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

### 2. Get Event Seats
```
GET /api/events/{event_id}/seats/

Response:
{
  "success": true,
  "seats": [
    {
      "id": 1,
      "seat_number": "A1",
      "status": "available",  // or "locked" or "reserved"
      "is_locked": false
    },
    {
      "id": 2,
      "seat_number": "A2",
      "status": "locked",     // User is selecting this seat
      "is_locked": true       // locked_until not yet expired
    }
  ]
}
```

---

### 3. Lock a Seat (SELECT FOR UPDATE HAPPENS HERE)
```
POST /api/events/{event_id}/seats/{seat_id}/lock/

Headers: 
  Authorization: Bearer {token}

Response:
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
```

**What happens inside**:
1. `transaction.atomic()` begins
2. `Seat.objects.select_for_update().get(...)` acquires lock
3. Check if seat is still available
4. Set `locked_until` to 5 minutes from now
5. Transaction ends, lock released
6. User has 5 minutes to confirm reservation or lock expires

---

### 4. Unlock a Seat
```
POST /api/events/{event_id}/seats/{seat_id}/unlock/

Response:
{
  "success": true,
  "message": "Seat A1 unlocked"
}
```

**When to use**: When user deselects a seat

---

### 5. Reserve Seats (Confirm Selection)
```
POST /api/events/{event_id}/reserve/

Body:
{
  "seat_ids": [1, 3, 5]
}

Response:
{
  "success": true,
  "message": "Successfully reserved 3 seat(s)",
  "reservation_id": 42,
  "seats": ["A1", "A3", "A5"]
}
```

**What happens inside**:
1. `transaction.atomic()` begins
2. Acquire locks on ALL selected seats
3. Verify all are locked by this user
4. Create Reservation object
5. Mark seats as 'reserved' instead of 'locked'
6. Release all locks

---

### 6. Get User's Reservations
```
GET /api/reservations/

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

---

### 7. Cancel Reservation
```
POST /api/reservations/{reservation_id}/cancel/

Response:
{
  "success": true,
  "message": "Reservation cancelled"
}
```

**What happens**: Seats revert to 'available' status

---

## 🚀 Setup & Running

### 1. Install Dependencies
```bash
cd /Users/bishalkumarshah/learning_django_basics/seat_reservation_workflow/seat_reservation

pip install django django-cors-headers
```

### 2. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Create Superuser
```bash
python manage.py createsuperuser
# Follow prompts to create admin account
```

### 4. Populate Sample Data
```bash
python manage.py populate_events
```

### 5. Run Django Server
```bash
python manage.py runserver
```

**Django will run on**: `http://localhost:8000`
**Admin panel**: `http://localhost:8000/admin`

---

## 🎨 React Frontend Setup

### 1. Create React App
```bash
cd /Users/bishalkumarshah/learning_django_basics/seat_reservation_workflow
npx create-react-app frontend
cd frontend
npm install axios
```

### 2. Key React Components

#### App.js (Main Component)
```javascript
import React, { useState, useEffect } from 'react';
import EventList from './components/EventList';
import SeatSelector from './components/SeatSelector';

function App() {
  const [events, setEvents] = useState([]);
  const [selectedEvent, setSelectedEvent] = useState(null);

  useEffect(() => {
    fetchEvents();
  }, []);

  const fetchEvents = async () => {
    const response = await fetch('http://localhost:8000/api/events/');
    const data = await response.json();
    setEvents(data.events);
  };

  return (
    <div className="container">
      <h1>🎬 Seat Reservation System</h1>
      {!selectedEvent ? (
        <EventList events={events} onSelect={setSelectedEvent} />
      ) : (
        <SeatSelector 
          event={selectedEvent} 
          onBack={() => setSelectedEvent(null)}
        />
      )}
    </div>
  );
}

export default App;
```

#### SeatSelector.js
```javascript
import React, { useState, useEffect } from 'react';
import './SeatSelector.css';

function SeatSelector({ event, onBack }) {
  const [seats, setSeats] = useState([]);
  const [selectedSeats, setSelectedSeats] = useState(new Set());
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSeats();
    const interval = setInterval(fetchSeats, 5000); // Poll every 5 seconds
    return () => clearInterval(interval);
  }, [event]);

  const fetchSeats = async () => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/events/${event.id}/seats/`,
        {
          credentials: 'include'
        }
      );
      const data = await response.json();
      setSeats(data.seats);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching seats:', error);
    }
  };

  const handleSeatClick = async (seat) => {
    if (seat.status === 'available') {
      // Lock the seat
      try {
        const response = await fetch(
          `http://localhost:8000/api/events/${event.id}/seats/${seat.id}/lock/`,
          {
            method: 'POST',
            credentials: 'include',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': getCookie('csrftoken')
            }
          }
        );
        const data = await response.json();
        if (data.success) {
          selectedSeats.add(seat.id);
          setSelectedSeats(new Set(selectedSeats));
          fetchSeats();
        }
      } catch (error) {
        console.error('Error locking seat:', error);
      }
    }
  };

  const handleReserve = async () => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/events/${event.id}/reserve/`,
        {
          method: 'POST',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
          },
          body: JSON.stringify({
            seat_ids: Array.from(selectedSeats)
          })
        }
      );
      const data = await response.json();
      if (data.success) {
        alert('✅ Seats reserved successfully!');
        onBack();
      } else {
        alert('❌ ' + data.error);
      }
    } catch (error) {
      console.error('Error reserving seats:', error);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="seat-selector">
      <h2>{event.name}</h2>
      <div className="seats-grid">
        {seats.map(seat => (
          <button
            key={seat.id}
            className={`seat ${seat.status} ${selectedSeats.has(seat.id) ? 'selected' : ''}`}
            onClick={() => handleSeatClick(seat)}
            disabled={seat.status !== 'available'}
          >
            {seat.seat_number}
          </button>
        ))}
      </div>
      {selectedSeats.size > 0 && (
        <button className="reserve-btn" onClick={handleReserve}>
          Reserve {selectedSeats.size} Seat(s)
        </button>
      )}
      <button className="back-btn" onClick={onBack}>Back</button>
    </div>
  );
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

export default SeatSelector;
```

#### SeatSelector.css
```css
.seat-selector {
  max-width: 800px;
  margin: 20px auto;
}

.seats-grid {
  display: grid;
  grid-template-columns: repeat(10, 1fr);
  gap: 10px;
  margin: 30px 0;
  padding: 20px;
  background: #f5f5f5;
  border-radius: 8px;
}

.seat {
  padding: 15px;
  border: 2px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.3s;
}

.seat.available {
  background: #4CAF50;
  color: white;
}

.seat.available:hover {
  background: #45a049;
  transform: scale(1.05);
}

.seat.available.selected {
  background: #2196F3;
  border-color: #0b7dda;
}

.seat.reserved {
  background: #f44336;
  color: white;
  cursor: not-allowed;
}

.seat.locked {
  background: #ff9800;
  color: white;
  cursor: not-allowed;
}

.reserve-btn {
  background: #2196F3;
  color: white;
  padding: 12px 30px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  font-weight: bold;
}

.reserve-btn:hover {
  background: #0b7dda;
}

.back-btn {
  margin-left: 10px;
  background: #666;
  color: white;
  padding: 12px 30px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
```

---

## 🔍 Understanding the Flow - Step by Step

### Scenario: User Alice reserves seats A1 and A2

```
STEP 1: Browse Events
┌─────────────────────────────────────────────┐
│ GET /api/events/                            │
│ Django fetches all Event objects            │
│ Returns events with seat counts             │
└─────────────────────────────────────────────┘
Alice sees "The Matrix - 45 available"

STEP 2: Select Event & View Seats
┌─────────────────────────────────────────────┐
│ GET /api/events/1/seats/                    │
│ Django fetches all Seat objects for event 1 │
│ Returns seat grid with statuses             │
└─────────────────────────────────────────────┘
Alice sees seat grid with available seats

STEP 3: Lock Seat A1 (SELECT FOR UPDATE!)
┌─────────────────────────────────────────────┐
│ POST /api/events/1/seats/1/lock/            │
│                                             │
│ Django starts transaction:                  │
│ ├─ SELECT FOR UPDATE Seat#1                 │
│ │  (Database locks this row)                │
│ ├─ Check: seat.status == 'available'? ✓    │
│ ├─ Check: seat.is_locked()? ✗              │
│ ├─ Set seat.locked_until = now + 5min      │
│ ├─ Set seat.locked_by = alice              │
│ ├─ Set seat.status = 'locked'              │
│ └─ COMMIT (lock released)                  │
└─────────────────────────────────────────────┘
Alice's seat A1 is now locked for 5 minutes

STEP 4: Lock Seat A2 (Same Process)
┌─────────────────────────────────────────────┐
│ POST /api/events/1/seats/2/lock/            │
│ Same as Step 3 for Seat#2                   │
└─────────────────────────────────────────────┘
Alice's seat A2 is now locked for 5 minutes

STEP 5: Confirm Reservation (All Locks Together)
┌─────────────────────────────────────────────┐
│ POST /api/events/1/reserve/                 │
│ body: { seat_ids: [1, 2] }                  │
│                                             │
│ Django starts transaction:                  │
│ ├─ SELECT FOR UPDATE Seat#1, Seat#2        │
│ │  (Database locks BOTH rows)               │
│ ├─ Check: all locked by alice? ✓           │
│ ├─ Create Reservation(alice, event1)        │
│ ├─ Add seats [1, 2] to reservation          │
│ ├─ For each seat:                           │
│ │  ├─ seat.status = 'reserved'              │
│ │  ├─ seat.reserved_by = alice              │
│ │  ├─ seat.reserved_at = now                │
│ │  └─ Clear locked_until & locked_by        │
│ └─ COMMIT (locks released)                 │
└─────────────────────────────────────────────┘
Alice's reservation confirmed! Seats A1, A2 are permanent

STEP 6: View Reservations
┌─────────────────────────────────────────────┐
│ GET /api/reservations/                      │
│ Django fetches Reservation objects for user │
│ Returns all confirmed reservations          │
└─────────────────────────────────────────────┘
Alice sees her confirmed reservation
```

---

## ⚠️ What Happens If Lock Expires

If Alice selects seats but doesn't confirm within 5 minutes:

```python
# Automatic expiration happens when:
# - Another user tries to lock the seat
# - Admin checks the seat status
# - Seat is accessed in any way

def is_locked(self):
    if self.locked_until is None:
        return False
    if timezone.now() < self.locked_until:  # Still locked
        return True
    else:
        return False  # Expired! Treat as available
```

A background task (or periodic cleanup) can reset expired locks:

```python
# In a management command or Celery task
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

## 🧪 Testing the Lock Mechanism

### Test Case 1: Basic Locking
```bash
# Terminal 1: User Alice
curl -X POST http://localhost:8000/api/events/1/seats/1/lock/ \
  -H "Content-Type: application/json"

# Should succeed
```

### Test Case 2: Concurrent Access (Race Condition Test)
```bash
# Terminal 1: User Alice tries to lock same seat
for i in {1..5}; do
  curl -X POST http://localhost:8000/api/events/1/seats/1/lock/ &
done
wait

# Only ONE should succeed due to database-level locking
```

### Test Case 3: Check Lock Status
```bash
# Check if seat is locked
curl http://localhost:8000/api/events/1/seats/1/ | grep "is_locked"

# Should show: "is_locked": true
```

---

## 🎯 Key Takeaways

1. **`select_for_update()`** = Database-level row locking
2. **`transaction.atomic()`** = Ensures atomicity (all-or-nothing)
3. **`locked_until`** field = Temporary hold expiration
4. **Status progression**: available → locked → reserved
5. **Race condition prevention**: No two users can modify same seat simultaneously
6. **Lock timeout**: Automatically handled by checking `locked_until` timestamp

---

## 📝 Django Admin Features

Visit `http://localhost:8000/admin/` to:
- Create/edit events
- View all seats and their status
- Monitor reservations
- Check who locked/reserved seats
- See lock expiration times

---

This system is production-ready for moderate scale applications! For very high-volume systems, consider:
- PostgreSQL (better locking)
- Redis for session/cache
- Celery for background tasks
- Real-time updates with WebSockets
