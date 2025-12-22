# 🎬 React + Django Integration - Visual Quick Guide

## One-Minute Overview

```
┌─────────────────────────────┐
│   USER (Browser)            │
│   Sees Beautiful UI          │
│   Clicks buttons             │
└────────────┬────────────────┘
             │ Click "Lock Seat A1"
             │
             ▼
┌─────────────────────────────┐
│   REACT (JavaScript)        │     
│   ├─ Detects click          │
│   ├─ Gets seat data         │
│   ├─ Prepares request       │
│   └─ Calls axios.post()     │
└────────────┬────────────────┘
             │ HTTP POST
             │ http://localhost:8000/api/events/1/seats/1/lock/
             │ {
             │   headers: {X-CSRFToken: ...},
             │   cookie: sessionid=...
             │ }
             │
             ▼
┌─────────────────────────────┐
│   DJANGO (Python)           │
│   ├─ Receives request       │
│   ├─ Checks authentication  │
│   ├─ START transaction      │
│   ├─ SELECT FOR UPDATE      │
│   │  (lock seat row)        │
│   ├─ Verify: available?     │
│   ├─ UPDATE locked_until    │
│   ├─ COMMIT transaction     │
│   └─ Return JSON            │
└────────────┬────────────────┘
             │ HTTP Response
             │ {
             │   "success": true,
             │   "seat": {
             │     "id": 1,
             │     "status": "locked",
             │     "locked_until": "10:05:00"
             │   }
             │ }
             │
             ▼
┌─────────────────────────────┐
│   REACT (JavaScript)        │
│   ├─ Receives response      │
│   ├─ Parses JSON            │
│   ├─ Updates state          │
│   ├─ Triggers re-render     │
│   └─ Shows blue seat        │
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│   USER (Browser)            │
│   Sees Seat A1 is BLUE      │
│   "Locked for 5 minutes"    │
└─────────────────────────────┘
```

---

## API vs Frontend

### What React Does
```javascript
// React Components
// ├─ Display UI
// ├─ Handle clicks/input
// ├─ Store local state
// ├─ Make HTTP requests
// └─ Update UI based on responses

Example: SeatSelector.js
├─ Displays 60 seats
├─ User clicks seat
├─ Sends axios.post() request
├─ Waits for response
└─ Updates UI color
```

### What Django Does
```python
# Django Views
# ├─ Receive HTTP requests
# ├─ Authenticate users
# ├─ Execute business logic
# ├─ Lock database rows
# ├─ Query/update database
# └─ Return JSON responses

Example: lock_seat() view
├─ Receives POST request
├─ Checks user authentication
├─ Starts transaction
├─ Locks seat row (SELECT FOR UPDATE)
├─ Verifies seat is available
├─ Updates seat status
└─ Returns JSON
```

---

## The "Special Sauce": SELECT FOR UPDATE

### Why Django?

```javascript
// React CAN'T do this:
axios.post('/api/lock/', {seat_id: 1})

// Why? Because:
// ❌ React can't talk directly to database
// ❌ React can't acquire row-level locks
// ❌ Multiple browsers would conflict

// Solution: Django does it!
// ✅ Django talks to database
// ✅ Django acquires locks
// ✅ Django prevents conflicts
```

### The Flow for Lock_Seat

```
Browser Tab 1          Browser Tab 2              Django Server          Database
(Alice)                (Bob)                      (port 8000)            (SQLite)
──────────────         ─────────────              ──────────────         ─────────

User clicks            
"Lock A1"              
    │                                            
    ├─ axios.post('/api/.../lock/') ─────────────────────────┐                
    │                                                          │            
    │                                                          ▼            
    │                                          lock_seat(request):       
    │                                          ├─ Start transaction      
    │                                          ├─ SELECT FOR UPDATE      
    │                                          │                         ├─ LOCK Seat#1
    │                                          │                         │ (exclusive)
    │                                          ├─ Check status           
    │                                          │  == "available"? YES ✓   
    │                                          ├─ UPDATE locked_until    
    │                                          │                         ├─ ROW LOCKED
    │                                          ├─ COMMIT                 
    │                                          │                         ├─ LOCK RELEASED
    │                                          ├─ Return success ────────┐
    │◄────────────────────────────────────────────────────────────────────┘
    │
    ├─ React updates state
    │  Seat A1 = BLUE
    │
User sees "Locked"
    │
    │
    │                   User clicks
    │                   "Lock A1"
    │                       │
    │                       ├─ axios.post('/api/.../lock/') ─────────────┐
    │                       │                                             │
    │                       │                                             ▼
    │                       │                                 lock_seat(request):
    │                       │                                 ├─ Start transaction
    │                       │                                 ├─ SELECT FOR UPDATE
    │                       │                                 │  (WAITS FOR LOCK!)
    │                       │                                 │
    │◄──────────────────────┤                                 │
    │ (Lock expires after                                      │
    │  5 minutes or                                            │
    │  user confirms)                                          │
    │ COMMIT ────────────────────────────────┐               │
    │                                         │               │
    │                                         ▼               │
    │                                  Database releases lock │
    │                                         │               │
    │                                         └──────────────►├─ LOCK RELEASED
    │                                                         │
    │                                         Now Bob's      │
    │                                         SELECT         │
    │                                         acquires lock  │
    │                                             │           │
    │                                             ├─ Read    ├─ Bob sees "locked"
    │                                             │  status │  (Alice has it)
    │                                             │ "locked"│
    │                                             │          │
    │                                    Return error ──────┐
    │                                       │                │
    │                       ◄────────────────┼────────────────┘
    │                       │
    │                   React shows:
    │                   "❌ Locked by another"
    │
User sees error ✅
```

---

## Request-Response Cycle

### Step 1: React Prepares Request

```javascript
// In React component
const handleSeatClick = async (seat) => {
  // 1. Check what action to take
  if (seat.status === 'available') {
    // 2. Prepare request
    const requestData = {};
    
    // 3. Prepare headers
    const headers = {
      'X-CSRFToken': getCookie('csrftoken'),
      'Content-Type': 'application/json'
    };
    
    // 4. Make request
    const response = await axios.post(
      `http://localhost:8000/api/events/1/seats/${seat.id}/lock/`,
      requestData,
      { headers, withCredentials: true }
    );
    
    // 5. Handle response
    if (response.data.success) {
      setSeats(updatedSeats);  // Update state
      setSelectedSeats(...);    // Update selection
    }
  }
};
```

### Step 2: Network Transport

```
HTTP Protocol (Hypertext Transfer Protocol)

REQUEST:
─────────────────────────────────────────
POST /api/events/1/seats/1/lock/ HTTP/1.1
Host: localhost:8000
Content-Type: application/json
X-CSRFToken: abc123xyz...
Cookie: sessionid=def456...
Content-Length: 2

{}

RESPONSE:
─────────────────────────────────────────
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 145
Set-Cookie: sessionid=def456...; Path=/

{
  "success": true,
  "message": "Seat A1 locked for 5 minutes",
  "seat": {
    "id": 1,
    "seat_number": "A1",
    "status": "locked",
    "locked_until": "2025-12-21T10:05:00Z"
  }
}
```

### Step 3: Django Processes

```python
# urls.py routes request to view
# POST /api/events/1/seats/1/lock/ → lock_seat(request, 1, 1)

@csrf_exempt
@require_http_methods(["POST"])
def lock_seat(request, event_id, seat_id):
    # 1. Get authenticated user from session
    user = request.user  # Auto-populated from sessionid cookie
    if not user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, 401)
    
    # 2. Start atomic transaction (all-or-nothing)
    with transaction.atomic():
        # 3. ACQUIRE DATABASE LOCK
        seat = Seat.objects.select_for_update().get(
            id=seat_id, 
            event_id=event_id
        )
        # ^ Database locks this row exclusively
        
        # 4. VERIFY CONDITIONS (safe because row is locked)
        if seat.status != 'available':
            return JsonResponse({'error': 'Not available'}, 400)
        
        if seat.is_locked():
            return JsonResponse({'error': 'Locked by another'}, 400)
        
        # 5. UPDATE DATABASE
        seat.locked_until = timezone.now() + timedelta(seconds=300)
        seat.locked_by = user
        seat.status = 'locked'
        seat.save()
        
        # 6. COMMIT TRANSACTION (lock automatically released)
    
    # 7. RETURN RESPONSE
    return JsonResponse({
        'success': True,
        'message': f'Seat {seat.seat_number} locked for 5 minutes',
        'seat': {
            'id': seat.id,
            'seat_number': seat.seat_number,
            'status': seat.status,
            'locked_until': seat.locked_until.isoformat()
        }
    })
```

### Step 4: React Handles Response

```javascript
// Response arrives
response = {
  success: true,
  message: 'Seat A1 locked...',
  seat: {...}
}

// React updates state
setSeats(prevSeats => 
  prevSeats.map(s => 
    s.id === 1 ? {
      ...s, 
      status: 'locked',
      is_locked: true
    } : s
  )
);

setSelectedSeats(prev => {
  prev.add(1);
  return new Set(prev);
});

// React re-renders component
// Virtual DOM → Real DOM → Browser updates UI
// User sees Seat A1 in BLUE
```

---

## Communication Protocol

### JSON Format

```javascript
// React sends this JavaScript object:
{
  seat_ids: [1, 3, 5],
  event_date: "2025-12-21"
}

// axios converts to JSON string
'{"seat_ids":[1,3,5],"event_date":"2025-12-21"}'

// Over HTTP as request body
// Django receives as:
request.body = b'{"seat_ids":[1,3,5],"event_date":"2025-12-21"}'

// Django parses back to Python dict
data = json.loads(request.body)
# data = {'seat_ids': [1, 3, 5], 'event_date': '2025-12-21'}

// Django creates response JSON
response_data = {
    'success': True,
    'reservation_id': 42,
    'seats': ['A1', 'A3', 'A5']
}

// Django converts to JSON string
# JsonResponse automatically does this!
'{"success":true,"reservation_id":42,"seats":["A1","A3","A5"]}'

// Over HTTP back to React
// React parses automatically via axios
response.data = {success: true, ...}
```

---

## Error Handling Flow

```
React tries to lock seat
        │
        ├─ axios.post('/api/.../lock/')
        │
        ▼
Django receives request
        │
        ├─ Check: user authenticated? NO ❌
        │
        └─ return JsonResponse(
             {'success': False, 'error': 'Not authenticated'},
             status=401
           )

React receives error response
        │
        ├─ response.status = 401
        │
        ├─ axios .catch() triggered
        │
        ├─ error.response.data = {
             'success': False,
             'error': 'Not authenticated'
           }
        │
        └─ showMessage('❌ Not authenticated', 'error')

User sees error message
        └─ "❌ Not authenticated"
```

---

## Authentication Flow

```
1. User enters username & password
   └─ React state: {username: "admin", password: "***"}

2. User clicks "Sign In"
   └─ axios.post('/api/login/', {username, password})

3. Django receives request
   ├─ Parse JSON
   ├─ Authenticate: django.contrib.auth.authenticate()
   │  ├─ Check user exists in database
   │  ├─ Check password matches
   │  └─ Returns User object if valid
   │
   ├─ Create session
   │  ├─ Generate random sessionid
   │  ├─ Store in database
   │  └─ Set-Cookie header in response
   │
   └─ Return JSON: {success: true, user_id: 1}

4. Browser receives response
   ├─ Parses JSON
   ├─ Stores session cookie (httpOnly, secure)
   └─ axios.defaults.withCredentials = true
      (future requests auto-include cookie)

5. User is now "logged in"
   ├─ For all future requests
   ├─ Browser sends sessionid cookie
   ├─ Django reads cookie
   ├─ Looks up session in database
   ├─ Identifies user
   └─ Sets request.user automatically

6. All requests are authenticated!
   └─ No need to send username/password again
```

---

## State Synchronization

```
React State            ←→    Django Database
─────────────────────────────────────────────

events = [
  {id: 1, name: "Matrix"},
  {id: 2, name: "Taylor Swift"}
]
                       ←      SELECT * FROM event

selectedSeats = Set([1, 3])
                       ←      Derived from:
                              SELECT * FROM seat
                              WHERE id IN (1, 3)
                              AND locked_by = user

isLoggedIn = true
                       ←      Derived from:
                              SELECT * FROM session
                              WHERE sessionid = cookies.sessionid

reservations = [{...}]
                       ←      SELECT * FROM reservation
                              WHERE user_id = 1
```

---

## Why This Works So Well

```
✅ React = Presentation Layer
   ├─ Beautiful, responsive UI
   ├─ Fast client-side rendering
   └─ Smooth user interactions

✅ Django = Business Logic Layer
   ├─ Secure authentication
   ├─ Database transactions
   ├─ Row-level locking (SELECT FOR UPDATE)
   └─ Data validation & integrity

✅ API = Communication Layer
   ├─ RESTful endpoints
   ├─ JSON data format
   ├─ HTTP protocol
   └─ CSRF protection

✅ Together = Complete Application
   ├─ Beautiful & Functional
   ├─ Secure & Reliable
   ├─ Scalable & Maintainable
   └─ Professional-grade system
```

---

## In Summary

```
User Browser (React)
        │
        │ Click
        ▼
React Event Handler
        │
        │ axios.post()
        ▼
HTTP Request
        │
        │ Over Internet
        ▼
Django Server
        │
        │ Views process request
        │ Database operations
        │ SELECT FOR UPDATE locking
        ▼
JSON Response
        │
        │ Over Internet
        ▼
React Receives Response
        │
        │ Update state
        ▼
Component Re-render
        │
        │ Virtual DOM
        ▼
Browser Updates UI
        │
        ▼
User Sees Result

✅ Complete cycle!
```

This is **modern web development** at its finest! 🚀
