# 🗄️ How React & Django Interact with Database

## 🎯 Quick Answer

```
DATABASE (SQLite)
       │
       ├─ Django CAN access directly ✅
       │  └─ Uses ORM (Object-Relational Mapping)
       │
       └─ React CANNOT access directly ❌
          └─ React runs in BROWSER (no database access)
          └─ React must use Django API to access database
```

---

## 🏗️ The Architecture

```
┌─────────────────────────────────────┐
│        REACT (Browser)              │
│      Port 3000 (JavaScript)         │
│                                     │
│  ❌ No direct database access       │
│  ❌ No file system access           │
│  ❌ No server-side code execution   │
│                                     │
│  ✅ Can make HTTP requests          │
│  ✅ Can call Django API endpoints   │
│  ✅ Can display data received       │
└─────────────────────────────────────┘
              │
              │ HTTP/REST API
              │ (JSON over network)
              │
              ▼
┌─────────────────────────────────────┐
│       DJANGO (Server)               │
│     Port 8000 (Python)              │
│                                     │
│  ✅ Direct database access          │
│  ✅ Can execute Python code         │
│  ✅ Can perform business logic      │
│  ✅ Can access file system          │
│                                     │
│  Views (API endpoints):             │
│  • Receive requests from React      │
│  • Query database using ORM         │
│  • Process data                     │
│  • Send JSON response back          │
└─────────────────────────────────────┘
              │
              │ Django ORM
              │ (Python objects)
              │
              ▼
┌─────────────────────────────────────┐
│    DATABASE (SQLite/PostgreSQL)     │
│                                     │
│  Tables:                            │
│  • events                           │
│  • seats                            │
│  • reservations                     │
│  • users                            │
│  • sessions                         │
│                                     │
│  ✅ Only Django accesses directly   │
│  ❌ React cannot access directly    │
└─────────────────────────────────────┘
```

---

## 🔄 Why This Design?

### Why React CAN'T Access Database Directly

```
1. SECURITY RISK
   └─ JavaScript runs in browser (user's computer)
      └─ User could open DevTools and modify code 
      └─ User could access database credentials
      └─ Malicious users could delete/modify data
      └─ DISASTER! 💥

2. ARCHITECTURE
   └─ React is CLIENT-SIDE
      └─ Browser sandboxed (can't access files)
      └─ Can't open TCP connections to databases
      └─ Can only make HTTP requests

3. PERFORMANCE
   └─ Database on server (far away)
      └─ React shouldn't make thousands of queries
      └─ Django caches and optimizes queries
      └─ Django sends only needed data

4. BUSINESS LOGIC
   └─ Complex operations need server
      └─ Locking seats: SELECT FOR UPDATE
      └─ Atomic transactions: all-or-nothing
      └─ Authorization checks: is user allowed?
      └─ Only possible on server-side
```

### Why Django CAN Access Database

```
1. SECURITY
   └─ Server-side code (trusted)
      └─ Credentials hidden in settings.py
      └─ User can't see or modify code
      └─ Authentication & authorization enforced

2. DIRECT CONNECTION
   └─ Django server on same machine as database
      └─ Can use database driver directly
      └─ Direct TCP connection to database
      └─ Full access to SQL operations

3. CONTROL
   └─ Django validates all requests
      └─ Check: is user authenticated?
      └─ Check: does user own this reservation?
      └─ Check: is seat available?
      └─ Only then allow database changes

4. PERFORMANCE
   └─ Django optimizes queries
      └─ Use SELECT FOR UPDATE for locking
      └─ Use transactions for consistency
      └─ Cache results to reduce queries
```

---

## 💻 Real Example: How They Interact

### Scenario: User Wants to Reserve a Seat

```
┌─────────────────────────────────┐
│  REACT (Browser)                │
│  User clicks "Reserve"          │
└─────────────────────────────────┘
         │
         │ Can't access database directly!
         │ Must use Django API
         │
         ▼
┌─────────────────────────────────┐
│  REACT CODE:                    │
│                                 │
│  axios.post(                    │
│    '/api/events/1/reserve/',    │
│    {seat_ids: [5, 7]}           │
│  )                              │
└─────────────────────────────────┘
         │
         │ HTTP Request to Django
         │
         ▼
┌─────────────────────────────────┐
│  DJANGO (Server)                │
│  reserve_seats() view           │
│                                 │
│  def reserve_seats(request):    │
│    # Extract data from request  │
│    seat_ids = [5, 7]            │
│    user = request.user          │
└─────────────────────────────────┘
         │
         │ Django now has direct access!
         │
         ▼
┌─────────────────────────────────┐
│  DJANGO ORM:                    │
│                                 │
│  # Query database              │
│  seats = Seat.objects           │
│    .select_for_update()         │
│    .filter(id__in=[5, 7])       │
│                                 │
│  # Lock seats in database       │
│  # Verify they're available     │
│  # Update them to reserved      │
│  # Create Reservation object    │
└─────────────────────────────────┘
         │
         │ Django ORM translates to SQL
         │
         ▼
┌─────────────────────────────────┐
│  DATABASE OPERATIONS:           │
│                                 │
│  SELECT * FROM seats            │
│  WHERE id IN (5, 7)             │
│  FOR UPDATE;  ← Lock rows       │
│                                 │
│  UPDATE seats SET               │
│  status='reserved',             │
│  reserved_by_id=1               │
│  WHERE id IN (5, 7);            │
│                                 │
│  INSERT INTO reservations ...   │
└─────────────────────────────────┘
         │
         │ Database executes changes
         │ Django receives results
         │
         ▼
┌─────────────────────────────────┐
│  DJANGO RETURNS JSON:           │
│                                 │
│  {                              │
│    "success": true,             │
│    "reservation": {...},        │
│    "message": "Reserved!"       │
│  }                              │
└─────────────────────────────────┘
         │
         │ HTTP Response
         │
         ▼
┌─────────────────────────────────┐
│  REACT RECEIVES DATA:           │
│                                 │
│  response.data = {              │
│    success: true,               │
│    reservation: {...}           │
│  }                              │
│                                 │
│  // Update React state          │
│  setReservation(data)           │
│  // Re-render UI                │
│  showMessage("✅ Reserved!")     │
└─────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  BROWSER DISPLAYS UPDATE:       │
│                                 │
│  "Reservation Confirmed! ✅"    │
│                                 │
│  Seats turn GREEN (reserved)    │
└─────────────────────────────────┘
```

---

## 📊 Comparison Table

| Aspect | React | Django | Database |
|--------|-------|--------|----------|
| **Location** | Browser (client) | Server | Server |
| **Direct DB Access** | ❌ NO | ✅ YES | N/A |
| **Language** | JavaScript | Python | SQL |
| **Runs Where** | User's computer | Our server | Our server |
| **Can See Code** | ✅ YES (DevTools) | ❌ NO (hidden) | ❌ NO (hidden) |
| **Database Credentials** | ❌ No access | ✅ Has access | N/A |
| **Can Execute SQL** | ❌ NO | ✅ YES | N/A |
| **Speed** | Fast (local) | Medium (network) | Fastest (local) |
| **Security** | Low (public) | High (private) | Very High |
| **How Accesses DB** | Via HTTP API | Via ORM/SQL | Direct queries |
| **Example** | `axios.get(...)` | `Seat.objects.all()` | `SELECT * FROM...` |

---

## 🔐 Security: Why Direct Access is Dangerous

### ❌ If React Had Direct Database Access (DANGEROUS!)

```javascript
// In React (NEVER DO THIS!)
import sqlite3 from 'sqlite3';  // ❌ DON'T DO THIS!

// Credentials in JavaScript (EXPOSED!)
const db = new Database({
  host: 'localhost',
  username: 'admin',           // ❌ VISIBLE in DevTools!
  password: 'mypassword123',   // ❌ EXPOSED!
});

// User could open DevTools:
// 1. See all database credentials
// 2. Modify JavaScript code
// 3. Execute malicious queries
// 4. Delete all data!
// 5. Steal other users' data!

// DISASTER! 💥

// Example of what hacker could do:
const result = db.query(`
  DELETE FROM reservations;  // Delete all bookings!
  DROP TABLE seats;          // Delete seats table!
  SELECT * FROM users;       // Steal user data!
`);
```

### ✅ With Django (SECURE!)

```python
# In Django (CORRECT!)
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        # Credentials in settings.py (SERVER, not browser!)
    }
}

# views.py (Server-side, hidden from users)
@login_required  # ← Check: is user authenticated?
def reserve_seats(request):
    # Verify user owns these seats
    user = request.user
    
    # Check: can this user perform this action?
    if not user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, 401)
    
    # Only then access database
    seats = Seat.objects.select_for_update().filter(
        id__in=request.POST.get('seat_ids')
    )
    
    # Django prevents SQL injection:
    # Even if user sends malicious SQL, Django ORM escapes it
    # User can't execute arbitrary SQL
    
    # Return only necessary data to React
    return JsonResponse({
        'success': True,
        'reservation': serialized_data
    })

# React receives safe JSON response
# React can't do anything malicious with it
```

**Why this is secure:**

1. **Credentials hidden** - Only server knows password
2. **Code hidden** - User can't see business logic 
3. **Validation** - Server checks every request
4. **Authorization** - Server ensures user owns data
5. **SQL injection prevention** - ORM escapes dangerous input
6. **Rate limiting** - Server can block abuse
7. **Audit logging** - Server logs all changes

---

## 🔄 Complete Data Flow with Both

### Step 1: React Requests Events

```
┌──────────────┐
│     REACT    │
│              │
│ axios.get(   │
│   '/api/     │
│   events/'   │
│ )            │
└──────────────┘
       │
       │ HTTP GET request
       │ (Can't access database!)
       │
       ▼
┌──────────────────────────────────┐
│         DJANGO                   │
│                                  │
│ @app.get('/api/events/')         │
│ def get_events(request):         │
│   # Django accesses database ✅   │
│   events = Event.objects.all()   │
│                                  │
│   # Convert to JSON              │
│   return JsonResponse({          │
│     'events': [...]              │
│   })                             │
└──────────────────────────────────┘
       │
       │ JSON response
       │
       ▼
┌──────────────┐
│     REACT    │
│              │
│ response.data│
│ = [...]      │
│              │
│ setEvents()  │
│ Re-render UI │
└──────────────┘
```

### Step 2: React Locks a Seat

```
┌──────────────────────────┐
│         REACT            │
│                          │
│ User clicks Seat A1      │
│                          │
│ axios.post(              │
│   '/api/seats/5/lock/'   │
│ )                        │
│                          │
│ (Can't lock database!)   │
└──────────────────────────┘
       │
       │ HTTP POST request
       │
       ▼
┌────────────────────────────────────────┐
│           DJANGO                       │
│                                        │
│ @app.post('/api/seats/<id>/lock/')     │
│ def lock_seat(request, id):            │
│   with transaction.atomic():           │
│     # Django locks row in database ✅   │
│     seat = Seat.objects                │
│       .select_for_update()             │
│       .get(id=id)                      │
│                                        │
│     if seat.status != 'available':     │
│       return error()                   │
│                                        │
│     # Update database directly ✅      │
│     seat.locked_until = now + 5min     │
│     seat.locked_by = user              │
│     seat.save()  # ← Direct DB write   │
│                                        │
│   return JsonResponse({                │
│     'success': true,                   │
│     'seat': {...}                      │
│   })                                   │
└────────────────────────────────────────┘
       │
       │ JSON response
       │
       ▼
┌──────────────────────────┐
│         REACT            │
│                          │
│ Seat A1 turns BLUE       │
│ (Locked by you)          │
│                          │
│ Start countdown timer    │
└──────────────────────────┘
```

---

## 📋 Django's Database Access Methods

```python
# Method 1: Direct ORM Query
Event.objects.all()
# Django converts to: SELECT * FROM reservations_event;

# Method 2: Filtered Query
Seat.objects.filter(status='available')
# Django converts to: SELECT * FROM reservations_seat WHERE status='available';

# Method 3: Update
seat.status = 'locked'
seat.save()
# Django converts to: UPDATE reservations_seat SET status='locked' WHERE id=...;

# Method 4: Create
Reservation.objects.create(
    event_id=1,
    user=request.user,
    seats=[5, 7]
)
# Django converts to: INSERT INTO reservations_reservation (...) VALUES (...);

# Method 5: Row-Level Locking (SELECT FOR UPDATE)
Seat.objects.select_for_update().get(id=5)
# Django converts to: SELECT * FROM reservations_seat WHERE id=5 FOR UPDATE;
# Database LOCKS this row (exclusive access)

# Method 6: Raw SQL (if needed)
Seat.objects.raw('SELECT * FROM reservations_seat WHERE ...')
# Direct SQL query (less safe, but works)
```

---

## 🎯 Key Concepts

### React's Limitations

```
✅ CAN:
  • Make HTTP requests
  • Display data
  • Handle user input
  • Show/hide UI elements
  • Call Django API endpoints
  • Store data in localStorage (browser memory)

❌ CANNOT:
  • Access database
  • Access file system
  • Execute server-side code
  • See Django source code
  • Know database credentials
  • Perform SQL queries
  • Lock database rows
  • Use transactions
```

### Django's Capabilities

```
✅ CAN:
  • Query database directly
  • Use ORM (high-level)
  • Use raw SQL (low-level)
  • Lock rows (SELECT FOR UPDATE)
  • Use transactions (atomic operations)
  • Validate data
  • Enforce authentication
  • Check authorization
  • Execute Python code
  • Access file system
  • Log operations
  • Manage sessions

❌ SHOULD NOT:
  • Expose database credentials
  • Execute untrusted SQL
  • Trust client-side validation
  • Skip authentication checks
```

---

## 🚀 Typical Workflow

```
1. User opens React app
   └─ React = Client
   
2. User wants to see events
   └─ React can't query database directly
   └─ React must call Django API
   
3. React sends: GET /api/events/
   └─ Over HTTP network
   └─ Django receives request
   
4. Django accesses database
   └─ Uses ORM: Event.objects.all()
   └─ Gets all events from SQLite
   └─ Converts to JSON
   
5. Django sends: JSON response
   └─ React receives data
   └─ React updates state
   └─ React re-renders UI
   
6. User sees events on screen
   └─ React displays data
   
7. User clicks event
   └─ React wants to see seats
   └─ Repeat from step 3
   
8. User clicks seat
   └─ React wants to lock it
   └─ React calls: POST /api/seats/5/lock/
   
9. Django locks seat in database
   └─ SELECT FOR UPDATE
   └─ UPDATE status to 'locked'
   
10. React shows locked seat
    └─ Seat turns blue
```

---

## 📊 Summary Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                     THE BIG PICTURE                            │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  FRONTEND (React)              BACKEND (Django)   DATABASE     │
│  ─────────────────             ──────────────     ────────     │
│                                                                │
│  Runs in:                      Runs on:           Runs on:    │
│  Browser (User's PC)           Server             Server      │
│  Port 3000                     Port 8000          SQLite      │
│                                                                │
│  Access:                       Access:            Access:     │
│  ❌ No DB access               ✅ Full DB access  N/A          │
│  ✅ Call APIs                  ✅ All operations  (SQL only)   │
│  ✅ Display data               ✅ Validation                   │
│                                ✅ Authorization                │
│                                                                │
│  Communication:                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  React               HTTP/REST API        Django        │ │
│  │                                                          │ │
│  │  axios.post(         POST /api/lock/      view function │ │
│  │   .../lock/  ───────────────────────────>  def lock_... │ │
│  │  )                                                       │ │
│  │                      ← ← ← ← ← ← ← ←      Database ops │
│  │                   JSON response            (ORM query)  │ │
│  │                                                          │ │
│  │  setSeats(...)       ← ← ← ← ← ← ← ←      return JSON  │ │
│  │  Re-render           JSON data                          │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## 💡 Why This Design?

```
1. SECURITY ✅
   └─ Credentials on server only
   └─ Validation on server only
   └─ Authorization enforced on server

2. SCALABILITY ✅
   └─ Multiple Django servers can serve requests
   └─ Database querying optimized on server
   └─ Caching reduces database load

3. MAINTAINABILITY ✅
   └─ Frontend team (React) works independently
   └─ Backend team (Django) works independently
   └─ API contract defines communication

4. PERFORMANCE ✅
   └─ Browser doesn't handle heavy lifting
   └─ Server optimizes database queries
   └─ Network sends only needed data

5. STANDARDS ✅
   └─ REST API is industry standard
   └─ HTTP is universal
   └─ JSON is widely supported
```

---

**The key takeaway:**

```
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║  React: "Hey Django, get me the events!"                 ║
║         (Can't access database)                          ║
║                                                            ║
║  Django: "Sure, let me query the database for you..."    ║
║          (Accesses database directly)                    ║
║                                                            ║
║  Django: "Here are the events as JSON!"                  ║
║          (Sends response back)                           ║
║                                                            ║
║  React: "Thanks! Let me show this on screen!"            ║
║         (Renders UI with data)                           ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
```

**They work together but have different roles! 🤝**
