# 🔄 How Django and React Work Together

## 🎯 The Big Picture

```
┌─────────────────────────────────────────────────────────────┐
│                        YOUR BROWSER                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────────┐      ┌──────────────────────┐ │
│  │      React Frontend      │      │   Session/Auth       │ │
│  │   (localhost:3000)       │◄────►│   (Browser Cookie)   │ │
│  │                          │      │                      │ │
│  │ ┌────────────────────┐   │      └──────────────────────┘ │
│  │ │  LoginForm         │   │                                 │
│  │ │  EventList         │   │      ┌──────────────────────┐ │
│  │ │  SeatSelector      │   │      │  CSRF Token          │ │
│  │ │  UserReservations  │   │      │  (Security)          │ │
│  │ └────────────────────┘   │      │                      │ │
│  └──────────────────────────┘      └──────────────────────┘ │
│           │                                                    │
│           │                                                    │
│           │ HTTP Requests (JSON)                             │
│           │ + Cookies + CSRF Token                           │
│           │ (Secured)                                        │
│           ▼                                                    │
└─────────────────────────────────────────────────────────────┘
                        │
                        │
                        │  
        ┌───────────────┴───────────────┐
        │                               │
        │   (Over HTTP/HTTPS)           │
        │                               │
        ▼                               ▼
┌──────────────────────────┐    ┌──────────────────┐
│   Django Backend         │    │   Database       │
│  (localhost:8000)        │◄──►│   (SQLite)       │
│                          │    │                  │
│ ┌─────────────────────┐  │    └──────────────────┘
│ │  API Endpoints      │  │
│ │  ├─ /api/login/     │  │    Events, Seats,
│ │  ├─ /api/events/    │  │    Reservations
│ │  ├─ /api/seats/     │  │
│ │  └─ /api/reserve/   │  │
│ └─────────────────────┘  │
│                          │
│ ┌─────────────────────┐  │
│ │  Views Layer        │  │
│ │  (Handle requests)  │  │
│ └─────────────────────┘  │
│                          │
│ ┌─────────────────────┐  │
│ │  Models Layer       │  │
│ │  (Data + Logic)     │  │
│ └─────────────────────┘  │
└──────────────────────────┘
```

---

## 📡 Communication Protocol

### What React Does:
1. **Sends HTTP requests** to Django
2. **Includes authentication** (session cookie)
3. **Includes CSRF token** for security
4. **Receives JSON responses** from Django
5. **Updates UI** based on response

### What Django Does:
1. **Receives HTTP requests** from React
2. **Authenticates user** using session
3. **Validates CSRF token** for security
4. **Processes request** using views
5. **Returns JSON response** to React

---

## 🔐 Authentication Flow

```
STEP 1: LOGIN
═════════════════════════════════════════════════════════════

User enters credentials in React LoginForm:
  ┌────────────────────┐
  │  username: admin   │
  │  password: admin123│
  └────────────────────┘
         │
         ▼
React sends POST request:
  
  POST http://localhost:8000/api/login/
  {
    "username": "admin",
    "password": "admin123"
  }

         │
         ▼
Django receives request in login view:
  
  def login_api(request):
      username = request.POST.get('username')
      password = request.POST.get('password')
      user = authenticate(username=username, password=password)
      
      if user:
          login(request, user)  # ← Creates session
          return JsonResponse({"success": true, "user_id": user.id})
      return JsonResponse({"error": "Invalid credentials"})

         │
         ▼
Django creates SESSION COOKIE and sends back:
  
  HTTP/1.1 200 OK
  Set-Cookie: sessionid=abc123xyz789; Path=/; HttpOnly
  
  {
    "success": true,
    "user_id": 1
  }

         │
         ▼
React browser automatically stores sessionid cookie
Browser will include this cookie in all future requests


STEP 2: SUBSEQUENT REQUESTS (All authenticated now)
═════════════════════════════════════════════════════════════

React wants to lock a seat:

  POST http://localhost:8000/api/events/1/seats/5/lock/
  Headers: {
    "X-CSRFToken": "token_abc123",
    "Cookie": "sessionid=abc123xyz789"  ← Sent automatically
  }

         │
         ▼
Django receives request:
  
  @csrf_exempt  # or use CSRF middleware
  def lock_seat(request, event_id, seat_id):
      if not request.user.is_authenticated:
          return JsonResponse({"error": "Not authenticated"})
      
      # Proceed with locking...

         │
         ▼
Django uses session to identify user and locks seat
Returns JSON response

         │
         ▼
React receives response and updates UI
```

---

## 🔄 Complete Example: Locking a Seat

### Timeline (What happens second-by-second)

```
T=0s
────────────────────────────────────────────────────────────
User clicks on Seat A1 in React

T=0.05s
────────────────────────────────────────────────────────────
React Component (SeatSelector.js):

  handleSeatClick(seat_id) {
    axios.post(
      'http://localhost:8000/api/events/1/seats/5/lock/',
      {},
      {
        headers: {
          'X-CSRFToken': csrfToken,
        },
        withCredentials: true  // ← Include cookies
      }
    )
  }

T=0.1s
────────────────────────────────────────────────────────────
HTTP Request travels from React to Django:

  ┌─────────────────────────────────────────────────────────┐
  │  POST http://localhost:8000/api/events/1/seats/5/lock/  │
  ├─────────────────────────────────────────────────────────┤
  │  Headers:                                               │
  │  ├─ X-CSRFToken: abc123xyz789                           │
  │  ├─ Cookie: sessionid=def456uvw012                      │
  │  ├─ Content-Type: application/json                      │
  │  └─ Origin: http://localhost:3000                       │
  │                                                         │
  │  Body: {}                                               │
  └─────────────────────────────────────────────────────────┘

T=0.2s
────────────────────────────────────────────────────────────
Django receives in views.py:

  @csrf_exempt
  @require_http_methods(["POST"])
  def lock_seat(request, event_id, seat_id):
      
      # ✓ Verify user is logged in (from sessionid cookie)
      if not request.user.is_authenticated:
          return JsonResponse({"error": "Login required"}, status=401)
      
      # ✓ Verify CSRF token
      csrf_token = request.META.get('HTTP_X_CSRFTOKEN')
      
      # Start atomic transaction
      with transaction.atomic():
          
          # ⭐ LOCK THE ROW IN DATABASE
          seat = Seat.objects.select_for_update().get(
              id=seat_id, 
              event_id=event_id
          )
          
          # Check status
          if seat.status != 'available':
              return JsonResponse(
                  {"error": "Seat not available"},
                  status=400
              )
          
          # Lock it temporarily
          seat.locked_until = timezone.now() + timedelta(seconds=300)
          seat.locked_by = request.user
          seat.status = 'locked'
          seat.save()
      
      # Return success response
      return JsonResponse({
          "success": True,
          "message": "Seat locked for 5 minutes",
          "seat": {
              "id": seat.id,
              "seat_number": seat.seat_number,
              "status": "locked",
              "locked_until": seat.locked_until.isoformat()
          }
      })

T=0.3s
────────────────────────────────────────────────────────────
HTTP Response travels back from Django to React:

  ┌─────────────────────────────────────────────────────────┐
  │  HTTP/1.1 200 OK                                        │
  ├─────────────────────────────────────────────────────────┤
  │  Headers:                                               │
  │  ├─ Content-Type: application/json                      │
  │  ├─ Access-Control-Allow-Origin: http://localhost:3000 │
  │  └─ (other headers)                                     │
  │                                                         │
  │  Body:                                                  │
  │  {                                                      │
  │    "success": true,                                     │
  │    "message": "Seat locked for 5 minutes",              │
  │    "seat": {                                            │
  │      "id": 5,                                           │
  │      "seat_number": "A1",                               │
  │      "status": "locked",                                │
  │      "locked_until": "2025-12-22T10:05:30Z"             │
  │    }                                                    │
  │  }                                                      │
  └─────────────────────────────────────────────────────────┘

T=0.35s
────────────────────────────────────────────────────────────
React receives response in handleSeatClick callback:

  .then(response => {
      console.log("Seat locked!", response.data);
      
      // Update React state
      setSelectedSeats([...selectedSeats, {
          id: 5,
          seat_number: "A1",
          locked_until: "2025-12-22T10:05:30Z"
      }]);
      
      // Start countdown timer
      startCountdown(300); // 5 minutes
  })
  .catch(error => {
      console.error("Failed to lock:", error);
      alert(error.response.data.error);
  });

T=0.4s
────────────────────────────────────────────────────────────
React re-renders with updated UI:

  Before:
  ┌──────┐
  │ A1   │  ← Gray (available)
  └──────┘

  After:
  ┌──────┐
  │ A1   │  ← Blue (locked by you)
  │ 4:59 │  ← Countdown timer
  └──────┘
```

---

## 🗂️ File Mapping: Where Everything Lives

### React Side (Frontend)

```
seat_reservation_frontend/src/
│
├── App.js
│   └─ Main component that manages pages
│      ├─ Import components
│      ├─ Manage authentication state
│      └─ Handle navigation
│
├── components/
│   │
│   ├── LoginForm.js
│   │   └─ Sends POST /api/login/
│   │      Receives sessionid cookie
│   │      Stores in localStorage
│   │
│   ├── EventList.js
│   │   └─ Sends GET /api/events/
│   │      Displays all events
│   │      Includes sessionid cookie automatically
│   │
│   ├── SeatSelector.js  ⭐ MAIN
│   │   ├─ Sends GET /api/events/{id}/seats/
│   │   ├─ Sends POST /api/events/{id}/seats/{id}/lock/  ← SELECT FOR UPDATE
│   │   ├─ Sends POST /api/events/{id}/seats/{id}/unlock/
│   │   └─ Sends POST /api/events/{id}/reserve/
│   │      All include sessionid cookie
│   │
│   └── UserReservations.js
│       ├─ Sends GET /api/reservations/
│       └─ Sends POST /api/reservations/{id}/cancel/
│
└── (CSS files for styling)
```

### Django Side (Backend)

```
seat_reservation_workflow/seat_reservation/
│
├── manage.py
│
├── reservations/
│   │
│   ├── models.py
│   │   ├─ Event model
│   │   ├─ Seat model (with locked_until, locked_by)
│   │   └─ Reservation model
│   │
│   ├── views.py ⭐ MAIN
│   │   ├─ login_api()
│   │   │   └─ React LoginForm → receives sessionid cookie
│   │   │
│   │   ├─ event_list()
│   │   │   └─ React EventList → GET /api/events/
│   │   │
│   │   ├─ seat_list()
│   │   │   └─ React SeatSelector → GET /api/events/{id}/seats/
│   │   │
│   │   ├─ lock_seat() ⭐ USES SELECT FOR UPDATE
│   │   │   └─ React SeatSelector → POST /api/events/{id}/seats/{id}/lock/
│   │   │
│   │   ├─ reserve_seat()
│   │   │   └─ React SeatSelector → POST /api/events/{id}/reserve/
│   │   │
│   │   └─ user_reservations()
│   │       └─ React UserReservations → GET /api/reservations/
│   │
│   ├── urls.py
│   │   └─ Maps API endpoints to views
│   │
│   ├── admin.py
│   │   └─ Admin interface for managing data
│   │
│   └── migrations/
│       └─ Database schema changes
│
└── seat_reservation/
    │
    ├── settings.py
    │   ├─ CORS_ALLOWED_ORIGINS (allows localhost:3000)
    │   ├─ INSTALLED_APPS (includes 'reservations')
    │   └─ Database config
    │
    ├── urls.py
    │   └─ Routes requests to reservations app
    │
    └── wsgi.py
        └─ Server configuration
```

---

## 🔒 How Authentication & CSRF Work

### Session-Based Authentication

```
DJANGO:
├─ User provides credentials
├─ Django authenticates user
├─ Django creates a SESSION in database
├─ Django sends SESSION ID as COOKIE to browser
│
└─ Cookie stored in browser automatically

REACT:
├─ axios with withCredentials: true
├─ Browser automatically includes cookie in all requests
└─ Django uses cookie to identify user

DATABASE (Django):
├─ django_session table stores:
│  ├─ session_key: "abc123xyz789"
│  ├─ session_data: {...user_id...}
│  └─ expire_date: ...
└─ When React sends request with cookie,
   Django looks up session and gets user
```

### CSRF Protection

```
REACT sends:
  {
    "X-CSRFToken": "token_abc123",
    headers...
  }

DJANGO checks:
  if request.META['HTTP_X_CSRFTOKEN'] == session_csrf_token:
      Process request
  else:
      Reject (403 Forbidden)

WHY? Prevents Cross-Site Request Forgery attacks
```

---

## 🔄 Data Flow Diagram: Complete Reservation

```
┌─────────────────────────────────────────────────────────────┐
│                    REACT FRONTEND                           │
│              (User Interface in Browser)                    │
└─────────────────────────────────────────────────────────────┘
       │
       │ 1. User clicks "Reserve"
       │    (Calls handleReserve in SeatSelector.js)
       │
       ├─ Prepare data:
       │  ├─ event_id: 1
       │  ├─ seat_ids: [5, 7, 10]
       │  ├─ Selected seats
       │  └─ User info (from session)
       │
       ▼
   ┌───────────────────────────────────────────┐
   │   POST /api/events/1/reserve/             │
   │   {                                       │
   │     "seat_ids": [5, 7, 10],               │
   │     "payment_method": "card"              │
   │   }                                       │
   │   Headers: {                              │
   │     "X-CSRFToken": "...",                 │
   │     "Cookie": "sessionid=..."             │
   │   }                                       │
   └───────────────────────────────────────────┘
       │
       │ (HTTP request over network)
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│                  DJANGO BACKEND                             │
│         (Server Processing on Port 8000)                   │
└─────────────────────────────────────────────────────────────┘
       │
       ├─ 1. Receive request in reserve_seat() view
       │
       ├─ 2. Authenticate user (from sessionid cookie)
       │    request.user = <User object>
       │
       ├─ 3. Validate CSRF token (from X-CSRFToken header)
       │
       ├─ 4. Start transaction.atomic()
       │    (All-or-nothing database operation)
       │
       ├─ 5. For each seat_id in [5, 7, 10]:
       │    │
       │    ├─ SELECT FOR UPDATE (lock row)
       │    │
       │    ├─ Check:
       │    │  ├─ seat.status == 'locked'? ✓
       │    │  ├─ seat.locked_by == request.user? ✓
       │    │  └─ Lock not expired? ✓
       │    │
       │    ├─ Update:
       │    │  ├─ seat.status = 'reserved'
       │    │  ├─ seat.reserved_by = request.user
       │    │  ├─ seat.locked_until = None
       │    │  └─ seat.save()
       │    │
       │    └─ Create Reservation object
       │       ├─ event_id = 1
       │       ├─ user = request.user
       │       ├─ seats = [5, 7, 10]
       │       └─ save()
       │
       ├─ 6. Commit transaction (database locks released)
       │
       └─ 7. Return success response
          {
            "success": true,
            "reservation": {
              "id": 42,
              "event": "Concert XYZ",
              "seats": ["A1", "A3", "A6"],
              "total_price": "$150.00"
            }
          }
       │
       │ (HTTP response over network)
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│                    REACT FRONTEND                           │
│              (User Interface in Browser)                    │
└─────────────────────────────────────────────────────────────┘
       │
       ├─ 1. Receive response
       │
       ├─ 2. Check if success: true
       │
       ├─ 3. Update state:
       │    ├─ Clear selectedSeats
       │    ├─ Add reservation to reservations list
       │    └─ Show "Reservation Confirmed!" message
       │
       ├─ 4. Update UI:
       │    ├─ Seats change color to Green (reserved)
       │    ├─ Show confirmation popup
       │    └─ Redirect to UserReservations page
       │
       └─ User sees confirmation and can view reservation ✓
```

---

## 📊 State Management: React ↔ Django

### React State (Frontend)
```javascript
// In SeatSelector.js

const [selectedSeats, setSelectedSeats] = useState([]);
// Stores: which seats user clicked
// Updated: in handleSeatClick()
// Used by: render seat grid UI

const [seatData, setSeatData] = useState([]);
// Stores: current status of all seats from Django
// Updated: every 3 seconds via GET /api/events/{id}/seats/
// Example: {id: 5, seat_number: "A1", status: "locked", locked_by: "alice"}

const [userReservations, setUserReservations] = useState([]);
// Stores: current user's confirmed reservations
// Updated: via GET /api/reservations/
// Used by: UserReservations component

const [isAuthenticated, setIsAuthenticated] = useState(false);
// Stores: is user logged in?
// Updated: after successful /api/login/
// Used by: show LoginForm or show app
```

### Django State (Backend)
```python
# In Database (SQLite)

# Users table
User.objects.get(id=1)
# ├─ username: "alice"
# ├─ password_hash: "pbkdf2_sha256$..."
# └─ is_active: True

# Sessions table
Session.objects.get(session_key="abc123xyz789")
# ├─ session_key: "abc123xyz789"
# ├─ session_data: <pickled {user_id: 1, ...}>
# └─ expire_date: 2025-12-29 (7 days)

# Events table
Event.objects.get(id=1)
# ├─ name: "Concert XYZ"
# ├─ date: "2025-12-25 20:00"
# └─ price: 50.00

# Seats table
Seat.objects.get(id=5)
# ├─ event_id: 1
# ├─ seat_number: "A1"
# ├─ status: "locked"           ← Current state
# ├─ locked_until: "2025-12-22 10:05:30"
# ├─ locked_by_id: 1            ← User who locked it
# ├─ reserved_by_id: None       ← Will be filled after reserve
# └─ reserved_at: None

# Reservations table
Reservation.objects.get(id=42)
# ├─ event_id: 1
# ├─ user_id: 1
# ├─ seats: [5, 7, 10]
# ├─ created_at: "2025-12-22 10:00:00"
# └─ is_cancelled: False
```

---

## 🔄 Real-Time Updates: How React Stays Synced

```
T=0s: Alice's browser
├─ Sets selectedSeats = [5]
└─ Sends POST /api/events/1/seats/5/lock/

T=0.3s: Django database
├─ Seat #5 updated:
│  ├─ status = "locked"
│  ├─ locked_by = Alice
│  └─ locked_until = now + 5min

T=3s: Bob's browser (polling)
├─ Sends GET /api/events/1/seats/ (every 3 seconds)
└─ Receives updated seat list:
   {
     id: 5,
     seat_number: "A1",
     status: "locked",           ← Changed!
     locked_by: "alice",
     locked_until: "2025-12-22 10:05:30"
   }

T=3.2s: Bob's browser
├─ Sees Seat A1 is now Blue (locked)
├─ Shows "Locked by alice"
└─ Prevents Bob from selecting it

T=305s: Server
├─ Scheduled task checks: seat #5 lock expired?
├─ YES! locked_until < now
└─ Automatically set status back to "available"

T=308s: Bob's browser (polling)
├─ Sends GET /api/events/1/seats/ again
└─ Receives:
   {
     id: 5,
     seat_number: "A1",
     status: "available",        ← Back to available!
     locked_by: None,
     locked_until: None
   }

T=308.2s: Bob's browser
├─ Sees Seat A1 is now Gray (available again)
└─ Can now select it
```

---

## 🎬 Summary: The Interaction Model

| Aspect | React | Django |
|--------|-------|--------|
| **Runs On** | Browser (Port 3000) | Server (Port 8000) |
| **Language** | JavaScript | Python |
| **Main Job** | Display UI, Handle clicks | Process logic, Database access |
| **How They Talk** | HTTP requests (JSON) | HTTP responses (JSON) |
| **Authentication** | Sends session cookie | Validates session cookie |
| **Security** | Sends CSRF token | Validates CSRF token |
| **Data Access** | Calls API endpoints | Queries database |
| **State Storage** | Browser memory (useState) | Database (SQLite/PostgreSQL) |
| **Real-Time Sync** | Polling every 3s | No push (stateless) |

---

## 🚀 Key Takeaway

```
Think of Django as a BANK and React as a CUSTOMER:

React (Customer):
├─ "Hello, I want to reserve seats"
├─ Sends request: "Lock seat 5"
├─ Shows ID (session cookie)
└─ Waits for response

Django (Bank):
├─ Receives request
├─ Checks: "Are you logged in?" (validates cookie)
├─ Checks: "Is seat 5 available?" (queries database)
├─ Locks seat 5 (SELECT FOR UPDATE)
├─ Updates database (seat.status = "locked")
└─ Returns response: "Seat 5 is now locked"

React (Customer):
├─ Receives "success" response
├─ Updates UI: "Seat 5 is now selected"
└─ Shows countdown timer

User sees the change on screen! ✓
```

---

**React = Frontend (What you see)**
**Django = Backend (The brain that manages data)**
**Together = Full web application! 🎬**
