# 🔗 How Django and React Work Together - Complete Explanation

## 📊 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│              REACT FRONTEND (Port 3000)                    │
│              ─────────────────────────────                 │
│              • Runs in Browser (Client-Side)               │
│              • Manages UI & User Interactions              │
│              • Stores state (selectedSeats, events, etc.)  │
│              • Handles form inputs                         │
│                                                             │
│              Components:                                    │
│              ├─ LoginForm (Asks for username/password)    │
│              ├─ EventList (Shows available events)         │
│              ├─ SeatSelector (Interactive seat grid)       │
│              └─ UserReservations (Shows bookings)          │
│                                                             │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ HTTP/HTTPS Requests
                       │ (JSON data over internet)
                       │
        ┌──────────────▼──────────────┐
        │  REST API Calls via Axios   │
        │  (JavaScript HTTP client)    │
        └──────────────┬──────────────┘
                       │
                       │ Example URLs:
                       │ • POST /api/login/
                       │ • GET /api/events/
                       │ • POST /api/events/1/seats/1/lock/
                       │ • POST /api/events/1/reserve/
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│              DJANGO BACKEND (Port 8000)                    │
│              ──────────────────────────                    │
│              • Runs on Server (Server-Side)                │
│              • Processes API requests                      │
│              • Handles database locking (SELECT FOR UPDATE)│
│              • Manages authentication & authorization      │
│              • Performs business logic                     │
│                                                             │
│              API Endpoints (Views):                         │
│              ├─ @login_user → Authenticate                │
│              ├─ @get_events → List events                 │
│              ├─ @lock_seat → SELECT FOR UPDATE            │
│              ├─ @reserve_seats → Confirm reservation      │
│              └─ @get_user_reservations → Show bookings    │
│                                                             │
│              Database:                                      │
│              └─ SQLite (Event, Seat, Reservation tables)   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Complete Communication Flow

### Step-by-Step: User Logs In

```
REACT (Frontend)                          DJANGO (Backend)
────────────────────────────────────────────────────────────

User enters username & password
in LoginForm component
         │
         ▼
State: username="admin", password="***"
         │
         ▼
User clicks "Sign In" button
         │
         ▼
handleLogin() function triggered
         │
         ├─ Get CSRF token from cookies
         │
         ▼
axios.post(
  'http://localhost:8000/api/login/',
  {
    "username": "admin",
    "password": "admin123"
  },
  {
    headers: {
      'X-CSRFToken': csrfToken,
      'Content-Type': 'application/json'
    }
  }
)
         │
         ├─ HTTP POST Request sent
         │  over the internet
         │
         ▼ (Network travel time)
                                          Request arrives at
                                          Django server
                                          
                                          login_user() view
                                          processes request
                                          │
                                          ├─ Parse JSON data
                                          │  username="admin"
                                          │  password="admin123"
                                          │
                                          ├─ Authenticate user
                                          │  authenticate(
                                          │    username="admin",
                                          │    password="admin123"
                                          │  )
                                          │
                                          ├─ Check database
                                          │  ✓ User exists
                                          │  ✓ Password matches
                                          │
                                          ├─ Create session
                                          │  Set sessionid cookie
                                          │
                                          ├─ Return JSON response
                                          │  {
                                          │    "success": true,
                                          │    "user_id": 1,
                                          │    "username": "admin"
                                          │  }
                                          │
                                          ├─ HTTP 200 response
                                          │  + Set-Cookie header
                                          │
Response arrives back at
React component
         │
         ├─ Parse response
         │  {success: true, ...}
         │
         ├─ Save to localStorage
         │
         ├─ Update state
         │  setIsLoggedIn(true)
         │  setCurrentUser({username, id})
         │
         ├─ Store session cookie
         │  (browser does this automatically)
         │
         ▼
Re-render component
showing EventList instead
of LoginForm

✅ User is now logged in!
```

---

## 📡 HTTP Request Anatomy

### What React Sends

```javascript
// In SeatSelector.js - handleSeatClick() function

axios.post(
  'http://localhost:8000/api/events/1/seats/5/lock/',  // URL
  {},  // Request body (empty in this case)
  {
    withCredentials: true,  // Include cookies in request
    headers: {
      'X-CSRFToken': getCookie('csrftoken'),  // Security token
      'Content-Type': 'application/json'  // Data format
    }
  }
)
.then(response => {
  console.log(response.data);  // Handle success
})
.catch(error => {
  console.log(error);  // Handle error
});
```

**What actually gets sent over the network:**

```
POST /api/events/1/seats/5/lock/ HTTP/1.1
Host: localhost:8000
Content-Type: application/json
X-CSRFToken: abc123xyz789
Cookie: sessionid=abc123; csrftoken=abc123xyz789

{}
```

---

### What Django Receives

```python
# In views.py - lock_seat() function

@csrf_exempt  # Already checked CSRF token manually
@require_http_methods(["POST"])
def lock_seat(request, event_id, seat_id):
    # request.method = 'POST'
    # request.path = '/api/events/1/seats/5/lock/'
    # request.user = <User: admin> (from session cookie)
    # request.body = b'{}'
    # request.POST = QueryDict (empty)
    # request.META['HTTP_X_CSRFTOKEN'] = 'abc123xyz789'
    
    # Parse JSON body
    data = json.loads(request.body)
    # data = {}
```

---

### What Django Sends Back

```python
# Success response
return JsonResponse({
    'success': True,
    'message': 'Seat A1 locked for 5 minutes',
    'seat': {
        'id': 5,
        'seat_number': 'A1',
        'locked_until': '2025-12-21T10:05:00Z',
        'status': 'locked'
    }
})

# HTTP Response:
# HTTP/1.1 200 OK
# Content-Type: application/json
# {
#   "success": true,
#   "message": "Seat A1 locked for 5 minutes",
#   "seat": {...}
# }
```

**What React Receives:**

```javascript
response.data = {
    success: true,
    message: 'Seat A1 locked for 5 minutes',
    seat: {
        id: 5,
        seat_number: 'A1',
        locked_until: '2025-12-21T10:05:00Z',
        status: 'locked'
    }
}

// Then React updates state:
setSeats(updatedSeatsArray)  // Re-render UI
setSelectedSeats(newSet)      // Update selection
showMessage('✅ Seat A1 locked...', 'success')
```

---

## 🔐 Authentication & Session Management

### How Sessions Work

```
1. React sends login request
   ├─ Username & password
   └─ Django verifies credentials

2. Django creates session
   ├─ Generates random sessionid
   │  (e.g., "abc123def456...")
   │
   ├─ Stores session data in database
   │  {
   │    sessionid: "abc123def456...",
   │    user_id: 1,
   │    login_time: "2025-12-21T10:00:00",
   │    ...
   │  }
   │
   └─ Sends back Set-Cookie header
      Set-Cookie: sessionid=abc123def456...; 
                  Path=/; 
                  HttpOnly; 
                  Secure

3. Browser automatically stores cookie
   └─ Saves sessionid in browser storage

4. Every future request includes cookie
   ├─ React sends:
   │  Cookie: sessionid=abc123def456...
   │
   └─ Django receives:
      ├─ Reads sessionid from cookie
      ├─ Looks up session in database
      ├─ Identifies user automatically
      └─ request.user is now populated

5. User is "logged in" for future requests
   └─ No need to send username/password again!
```

### Example: After Login, Request Events

```
React Component:
axios.get('http://localhost:8000/api/events/')
         │
         ├─ Browser automatically adds cookie
         │  (withCredentials: true in axios config)
         │
         ▼ (Network)
            
Django Backend:
get_events(request):
    │
    ├─ Receive request with sessionid cookie
    │
    ├─ Look up session in database
    │
    ├─ Populate request.user
    │  request.user = <User: admin> ✓
    │  request.user.is_authenticated = True ✓
    │
    ├─ Check authentication
    │  if not user.is_authenticated:
    │    return JsonResponse({error: '...'}, 401)
    │
    ├─ User is authenticated! ✓
    │
    └─ Fetch events from database
       
React receives events JSON
└─ Updates state & re-renders
```

---

## 🎯 Real Example: Complete Reservation Flow

```
USER INTERACTION                 REACT STATE              DJANGO PROCESSING
─────────────────────────────────────────────────────────────────────────

User opens app
    │
    ▼
App loads
    │
    ├─ axios.get('/api/events/')
    │
    ▼                            events = []
                                 loading = true
                                                            ─────────────────
                                                            SELECT * FROM 
                                                            reservations_event
                                                            
                                                            Return 3 events
    │
    ◄──────────────────────────
    
    ▼                            events = [
                                   {id: 1, name: "Matrix"},
                                   {id: 2, name: "Taylor Swift"},
                                   {id: 3, name: "Python Conf"}
                                 ]

User clicks event #1
    │
    ▼
    axios.get('/api/events/1/seats/')
    
    ▼                            seats = []
                                 loading = true
                                                            ─────────────────
                                                            SELECT * FROM
                                                            reservations_seat
                                                            WHERE event_id = 1
                                                            
                                                            Calculate is_locked()
                                                            for each seat
                                                            
                                                            Return 60 seats
    │
    ◄──────────────────────────
    
    ▼                            seats = [
                                   {id: 1, seat_number: "A1", 
                                    status: "available", is_locked: false},
                                   {id: 2, seat_number: "A2",
                                    status: "reserved", is_locked: false},
                                   {id: 3, seat_number: "A3",
                                    status: "available", is_locked: false},
                                   ...
                                 ]

User clicks Seat #1 (A1)
    │
    ▼
    axios.post('/api/events/1/seats/1/lock/', {}, 
               {headers: {X-CSRFToken: ...}})
    
    ▼                            selectedSeats = Set([1])
                                                            ─────────────────
                                                            transaction.atomic():
                                                            ├─ SELECT FOR UPDATE
                                                            │  reservations_seat
                                                            │  WHERE id = 1
                                                            │  (DATABASE LOCKS ROW)
                                                            │
                                                            ├─ Check status
                                                            │  == 'available'? YES ✓
                                                            │
                                                            ├─ Check is_locked()
                                                            │  false? YES ✓
                                                            │
                                                            ├─ UPDATE seat
                                                            │  locked_until = now+5m
                                                            │  locked_by = user
                                                            │  status = 'locked'
                                                            │
                                                            ├─ COMMIT
                                                            │  (lock released)
                                                            │
                                                            └─ Return success
    │
    ◄──────────────────────────
    
    ▼                            Alert: "✅ Seat A1 locked"
                                 Seat A1 UI changes to BLUE

User clicks Seat #3 (A3)
    │
    ▼
    axios.post('/api/events/1/seats/3/lock/', {}, ...)
    
    ▼                            selectedSeats = Set([1, 3])
                                                            ─────────────────
                                                            Same process
                                                            Seat #3 locked
    │
    ◄──────────────────────────
    
    ▼                            Seat A3 UI changes to BLUE

User clicks "Confirm Reservation"
    │
    ▼
    axios.post('/api/events/1/reserve/', 
               {seat_ids: [1, 3]}, ...)
    
    ▼                            reserving = true
                                                            ─────────────────
                                                            transaction.atomic():
                                                            ├─ SELECT FOR UPDATE
                                                            │  WHERE id IN [1, 3]
                                                            │  (locks both rows)
                                                            │
                                                            ├─ Verify both
                                                            │  locked by user? YES ✓
                                                            │
                                                            ├─ CREATE Reservation
                                                            │  user = alice
                                                            │  event_id = 1
                                                            │  status = confirmed
                                                            │
                                                            ├─ Add seats to
                                                            │  reservation
                                                            │
                                                            ├─ UPDATE both seats
                                                            │  status = reserved
                                                            │  reserved_by = alice
                                                            │  reserved_at = now
                                                            │
                                                            ├─ COMMIT
                                                            │  (locks released)
                                                            │
                                                            └─ Return success
    │
    ◄──────────────────────────
    
    ▼                            Alert: "✅ Reserved!"
                                 currentView = 'reservations'
                                 
User sees their reservation
    │
    ▼
    axios.get('/api/reservations/')
                                                            ─────────────────
                                                            SELECT * FROM 
                                                            reservations_reservation
                                                            WHERE user_id = 1
                                                            PREFETCH seats
                                                            
                                                            Return reservation
    │
    ◄──────────────────────────
    
    ▼                            reservations = [{
                                   id: 42,
                                   event_name: "Matrix",
                                   seats: ["A1", "A3"],
                                   status: "confirmed",
                                   total_price: "$200"
                                 }]

UI Shows reservation ✅
```

---

## 🔌 How Axios Connects React to Django

### Axios Configuration (in App.js)

```javascript
import axios from 'axios';

// Define API base URL
const API_BASE = 'http://localhost:8000';

// Configure Axios globally
useEffect(() => {
  // 1. Get CSRF token from cookies
  const csrfToken = getCookie('csrftoken');
  
  // 2. Add CSRF token to all requests
  axios.defaults.headers.common['X-CSRFToken'] = csrfToken;
  
  // 3. Include credentials (cookies) in all requests
  axios.defaults.withCredentials = true;
  
  // Now all axios requests will have:
  // - CSRF token in headers
  // - Session cookie automatically included
  // - Credentials flag set
}, []);
```

### Making Requests

```javascript
// GET Request (fetch data)
axios.get(`${API_BASE}/api/events/`)
  .then(response => {
    // response.data = actual JSON from Django
    setEvents(response.data.events);
  })
  .catch(error => {
    // Handle errors (400, 401, 500, etc.)
    console.error(error.response.data.error);
  });

// POST Request (send data to backend)
axios.post(`${API_BASE}/api/events/1/reserve/`, 
  {
    seat_ids: [1, 3]  // Data to send
  },
  {
    headers: {
      'X-CSRFToken': getCookie('csrftoken')
    }
  }
)
  .then(response => {
    if (response.data.success) {
      showMessage('✅ Reserved!', 'success');
    }
  })
  .catch(error => {
    showMessage('❌ ' + error.response.data.error, 'error');
  });
```

---

## 🛡️ Security: CSRF Protection

### Why We Need It

```
Without CSRF protection (DANGEROUS):
Hacker's website makes request to:
POST /api/events/1/reserve/ 
  with seat_ids that hacker wants

Django would process it because 
browser auto-includes session cookie
```

### How We Prevent It

```javascript
// React sends CSRF token
axios.defaults.headers.common['X-CSRFToken'] = csrfToken;

// Django verifies token
@csrf_exempt  // We manually verify token
def lock_seat(request, event_id, seat_id):
    # Check X-CSRFToken header matches
    # Only then process the request
```

```
With CSRF protection (SAFE):
Hacker's website tries to make request
├─ No X-CSRFToken header
│  (only React knows the token)
│
└─ Django rejects request
   403 Forbidden
```

---

## 🔄 State Management Flow

```
React Component
    │
    ├─ State variables
    │  - events []
    │  - selectedSeats Set([])
    │  - isLoggedIn false
    │  - currentUser null
    │  - loading false
    │
    └─ Event handlers
       ├─ onClick → handleSeatClick()
       ├─ onSubmit → handleLogin()
       └─ onChange → setSelectedSeats()

When user interacts:
    │
    ├─ Event fires (e.g., onClick)
    │
    ├─ Handler function called
    │
    ├─ Axios request sent to Django
    │  (Backend processes request)
    │
    ├─ Response received
    │
    ├─ State updated
    │  setSeats(newSeats)
    │  setSelectedSeats(newSet)
    │
    └─ Component re-renders
       └─ React.render() with new state
          └─ UI updated on screen
```

---

## 📊 Data Flow Diagram

```
┌──────────────────────────────────────────────────────────┐
│                  REACT FRONTEND                          │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Components                                        │ │
│  │  ├─ LoginForm                                      │ │
│  │  ├─ EventList                                      │ │
│  │  ├─ SeatSelector ← User clicks here              │ │
│  │  └─ UserReservations                              │ │
│  └──────────────────────────────────────────────────┘ │
│           │                                             │
│           │ User interaction                           │
│           ▼                                             │
│  ┌────────────────────────────────────────────────────┐ │
│  │  State (JavaScript objects)                        │ │
│  │  {                                                 │ │
│  │    events: [{...}, {...}],                         │ │
│  │    selectedSeats: Set([1, 3]),                     │ │
│  │    isLoggedIn: true,                               │ │
│  │    currentUser: {username, id},                    │ │
│  │    loading: false                                  │ │
│  │  }                                                 │ │
│  └──────────────────────────────────────────────────┘ │
│           │                                             │
│           │ Need data from backend?                    │
│           ▼                                             │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Axios HTTP Client                                 │ │
│  │  ├─ axios.get('/api/events/')                      │ │
│  │  ├─ axios.post('/api/login/', {...})              │ │
│  │  └─ axios.post('/api/.../lock/', ...)             │ │
│  └──────────────────────────────────────────────────┘ │
│           │                                             │
│           │ HTTP requests (JSON)                       │
│           │ over internet                              │
└───────────┼──────────────────────────────────────────┘
            │
            │ TCP/IP Network
            │
            ▼
┌──────────────────────────────────────────────────────────┐
│                  DJANGO BACKEND                          │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │  URL Router (urls.py)                              │ │
│  │  Maps URL → View function                          │ │
│  │  /api/events/ → get_events()                       │ │
│  │  /api/.../lock/ → lock_seat()                      │ │
│  └──────────────────────────────────────────────────┘ │
│           │                                             │
│           ▼                                             │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Views (views.py)                                  │ │
│  │  ├─ Authentication check                           │ │
│  │  ├─ Business logic                                 │ │
│  │  ├─ Database queries                               │ │
│  │  └─ Return JSON response                           │ │
│  └──────────────────────────────────────────────────┘ │
│           │                                             │
│           ▼                                             │
│  ┌────────────────────────────────────────────────────┐ │
│  │  ORM Models (models.py)                            │ │
│  │  ├─ Event.objects.all()                            │ │
│  │  ├─ Seat.objects.select_for_update().get()         │ │
│  │  └─ Reservation.objects.create()                   │ │
│  └──────────────────────────────────────────────────┘ │
│           │                                             │
│           ▼                                             │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Database (SQLite)                                 │ │
│  │  └─ event, seat, reservation tables                │ │
│  └──────────────────────────────────────────────────┘ │
│                                                          │
└──────────────────────────────────────────────────────────┘
            ▲
            │ JSON response
            │ with data
            │
┌───────────┴──────────────────────────────────────────────┐
│                  REACT FRONTEND                          │
│           ▲                                              │
│           │ Response data received                       │
│           │                                              │
│  ┌────────┴──────────────────────────────────────────┐  │
│  │  Update State                                     │  │
│  │  setEvents(responseData.events)                   │  │
│  │  setSelectedSeats(newSet)                         │  │
│  │  setState({...})                                  │  │
│  └────────┬──────────────────────────────────────────┘  │
│           │                                              │
│           ▼                                              │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Re-render Components                            │   │
│  │  Component tree updates                          │   │
│  │  Virtual DOM → Real DOM                          │   │
│  └──────────────────────────────────────────────────┘   │
│           │                                              │
│           ▼                                              │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Browser Renders Updated UI                      │   │
│  │  User sees new data on screen                    │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## 🎯 Key Interactions Summary

| Action | React | Django | Database |
|--------|-------|--------|----------|
| **Login** | Send username/password | Authenticate user, create session | Store session data |
| **Load Events** | axios.get('/api/events/') | Query all events | SELECT * FROM event |
| **Load Seats** | axios.get('/api/events/1/seats/') | Query seats, check locks | SELECT * FROM seat |
| **Lock Seat** | axios.post('/api/.../lock/') | **SELECT FOR UPDATE**, verify, update | Lock row, UPDATE status |
| **Confirm** | axios.post('/api/reserve/') | **SELECT FOR UPDATE** multiple, create reservation | Lock rows, INSERT, UPDATE |
| **View Bookings** | axios.get('/api/reservations/') | Query user's reservations | SELECT * FROM reservation WHERE user |
| **Cancel** | axios.post('/api/reservations/.../cancel/') | Cancel, release seats | UPDATE seats back to available |

---

## 🔗 Connection Types

### Request Headers (React → Django)

```
POST /api/events/1/seats/5/lock/ HTTP/1.1
Host: localhost:8000
Content-Type: application/json
X-CSRFToken: abc123xyz789...
Cookie: sessionid=def456ghi789...; csrftoken=abc123xyz789...
Origin: http://localhost:3000
Referer: http://localhost:3000/
```

### Response Headers (Django → React)

```
HTTP/1.1 200 OK
Content-Type: application/json
Set-Cookie: sessionid=def456ghi789...; Path=/; HttpOnly
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Credentials: true
```

---

## 🎨 Why This Architecture?

### Separation of Concerns

```
React Handles:
├─ User Interface ✓
├─ User Interactions ✓
├─ Client-side state ✓
└─ Form validation ✓

Django Handles:
├─ Authentication ✓
├─ Database operations ✓
├─ Business logic ✓
├─ Data validation ✓
├─ Database locking ✓
└─ Security ✓

Neither handles the other's job!
```

### Benefits

```
✅ Scalability
   └─ Can run multiple Django servers
      behind a load balancer
    
✅ Reusability
   └─ Django API can serve mobile apps,
      desktop apps, other frontends
   
✅ Maintainability
   └─ Frontend & backend teams can
      work independently
    
✅ Performance
   └─ Frontend: Fast client rendering
   └─ Backend: Heavy lifting (locking,
      transactions, security)
   
✅ Security
   └─ Sensitive operations on server
      (sessions, authentication, DB ops)
   └─ Frontend can't be compromised
```

---

## 🚀 Complete Request Cycle Summary

```
1️⃣  User action in browser
    └─ Click "Lock Seat A1"

2️⃣  React event handler triggered
    └─ handleSeatClick(seat)

3️⃣  Axios makes HTTP request
    └─ POST /api/events/1/seats/1/lock/
       with sessionid cookie & CSRF token

4️⃣  Request travels over network
    └─ TCP/IP packets to localhost:8000

5️⃣  Django receives request
    └─ URL router matches path to view

6️⃣  View function processes request
    ├─ Check authentication
    │  (from sessionid cookie)
    │
    ├─ Start database transaction
    │
    ├─ Acquire row-level lock
    │  SELECT FOR UPDATE
    │
    ├─ Verify seat status
    │
    ├─ Update seat in database
    │  locked_until = now + 5min
    │
    └─ Return JSON response

7️⃣  Response travels back to React
    └─ HTTP 200 OK + JSON data

8️⃣  React receives response
    ├─ Parse JSON
    │
    ├─ Update state
    │  setSeats(newSeats)
    │  setSelectedSeats(Set([1]))
    │
    └─ Update UI message
       "✅ Seat A1 locked"

9️⃣  Component re-renders
    ├─ React.render() called
    │
    ├─ Virtual DOM updated
    │
    └─ Real DOM changed

🔟 Browser displays updated UI
   └─ User sees Seat A1 in blue color
      "Locked for 5 minutes"

✅ Complete cycle finished!
   User can now see their selection.
```

---

This is **client-server architecture** at its finest! 🎯

React handles **what** users see, Django ensures **data integrity** and **business logic**. Together, they create a seamless, secure, and scalable application.
