# 🎯 Step-by-Step: Implement Auto Lock Release

## ⚡ Quick Fix (5 minutes)

### Step 1: Run Manual Cleanup NOW

```bash
cd /Users/bishalkumarshah/learning_django_basics/seat_reservation_workflow/seat_reservation

python manage.py release_expired_locks
```

**Expected Output:**
```
✅ Released lock on Seat A1 (Event: Concert, was locked by admin)
✅ Released lock on Seat B3 (Event: Taylor Swift, was locked by admin)
...
✅ Total locks released: 19
```

### Step 2: Verify It Works

```bash
# Open React app
http://localhost:3000

# Try to lock the seats that were just released
# They should now be available! ✅
```

**Done!** Expired locks are cleaned up. 🎉

---

## 🟢 OPTION A: Auto-Release Every 3 Seconds (React)

### For: Quick testing, visible updates

### Step 1: Update SeatSelector.js

**File:** `seat_reservation_frontend/src/components/SeatSelector.js`

Find this code (around line 30):
```javascript
useEffect(() => {
    // Load seats when component mounts
    fetchSeats();
}, [eventId]);
```

**Replace with:**
```javascript
useEffect(() => {
    // Load seats when component mounts
    fetchSeats();
    
    // ✨ NEW: Refresh seats every 3 seconds
    // This automatically triggers cleanup + fetch
    const interval = setInterval(fetchSeats, 3000);
    
    return () => clearInterval(interval);
}, [eventId]);
```

### Step 2: Test It

```bash
# Terminal 1: Start React
cd seat_reservation_frontend
npm start

# Terminal 2: Start Django
cd seat_reservation_workflow/seat_reservation
python manage.py runserver

# In browser:
# 1. Lock some seats
# 2. Wait 5 minutes
# 3. Seats automatically become available ✅
# (You'll see them refresh every 3 seconds)
```

### Result
- Seats refresh every 3 seconds
- Expired locks released automatically
- UI updates in real-time
- Simple implementation ✅

---

## 🟡 OPTION B: Manual Refresh Button (User Control)

### For: User-initiated cleanup, dashboard-style app

### Step 1: Create API Endpoint in Django

**File:** `seat_reservation_workflow/seat_reservation/reservations/views.py`

Add this at the end:

```python
# ... existing imports ...
from django.utils import timezone

# ... existing views ...

@csrf_exempt
@require_http_methods(["POST"])
def release_expired_locks_api(request):
    """
    API endpoint to manually release expired locks
    Called from React button click
    """
    try:
        now = timezone.now()
        
        # Find expired locks
        expired_locks = Seat.objects.filter(
            status='locked',
            locked_until__isnull=False,
            locked_until__lt=now
        )
        
        count = expired_locks.count()
        
        # Release them
        expired_locks.update(
            status='available',
            locked_until=None,
            locked_by=None
        )
        
        return JsonResponse({
            'success': True,
            'count': count,
            'message': f'Released {count} expired locks'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
```

### Step 2: Add URL Route

**File:** `seat_reservation_workflow/seat_reservation/reservations/urls.py`

Find the `urlpatterns` list and add:

```python
# ... existing imports ...

urlpatterns = [
    # ... existing paths ...
    
    # ✨ NEW: Add this line
    path('api/release-expired-locks/', views.release_expired_locks_api, 
         name='release_expired_locks'),
]
```

### Step 3: Update SeatSelector Component

**File:** `seat_reservation_frontend/src/components/SeatSelector.js`

Add this function inside the component:

```javascript
// Helper function to get CSRF token
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

// ✨ NEW: Release expired locks function
const releaseExpiredLocks = async () => {
    try {
        const response = await axios.post(
            'http://localhost:8000/api/release-expired-locks/',
            {},
            { 
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                withCredentials: true 
            }
        );
        
        if (response.data.success) {
            alert(`✅ Released ${response.data.count} expired locks!`);
            // Refresh seat list
            fetchSeats();
        }
    } catch (error) {
        alert('❌ Error: ' + error.message);
    }
};
```

### Step 4: Add Button to UI

Find the render section and add:

```javascript
return (
    <div className="seat-selector">
        <div className="seat-header">
            <h2>Select Your Seats</h2>
            {/* ✨ NEW: Add this button */}
            <button 
                onClick={releaseExpiredLocks}
                className="refresh-btn"
            >
                🔄 Release Expired Locks
            </button>
        </div>
        
        {/* ... rest of component ... */}
    </div>
);
```

### Step 5: Add Button Styling

**File:** `seat_reservation_frontend/src/components/SeatSelector.css`

Add at the end:

```css
.seat-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.refresh-btn {
    padding: 10px 20px;
    background-color: #4CAF50;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 14px;
    transition: background-color 0.3s;
}

.refresh-btn:hover {
    background-color: #45a049;
}
```

### Step 6: Test It

```bash
# 1. Start Django & React
# 2. Click "🔄 Release Expired Locks" button
# 3. See count of locks released
# 4. Seat list auto-refreshes
```

### Result
- User has manual control
- Click button to release locks
- Useful for dashboard/admin view
- More visible feedback ✅

---

## 🔵 OPTION C: Auto-Release Every 60 Seconds (Backend)

### For: Production, set & forget

### Step 1: Install APScheduler

```bash
cd /Users/bishalkumarshah/learning_django_basics/seat_reservation_workflow/seat_reservation

pip install django-apscheduler
```

### Step 2: Create tasks.py

**File:** `reservations/tasks.py` (new file)

```python
"""
Background tasks for seat reservation system
"""
from django.utils import timezone
from reservations.models import Seat


def release_expired_locks():
    """
    Background task to release expired seat locks
    Called every 60 seconds by APScheduler
    """
    now = timezone.now()
    
    # Find expired locks
    expired_locks = Seat.objects.filter(
        status='locked',
        locked_until__isnull=False,
        locked_until__lt=now
    )
    
    count = expired_locks.count()
    
    if count > 0:
        # Release them
        expired_locks.update(
            status='available',
            locked_until=None,
            locked_by=None
        )
        
        print(f'✅ Auto-released {count} expired locks')
    
    return count
```

### Step 3: Update settings.py

**File:** `seat_reservation/settings.py`

Add to INSTALLED_APPS:
```python
INSTALLED_APPS = [
    # ... existing apps ...
    'django_apscheduler',
    'reservations',
]
```

Add at the end of file:
```python
# APScheduler Configuration
APSCHEDULER_DATETIME_FORMAT = "N j, Y, f:s a"
```

### Step 4: Update apps.py

**File:** `reservations/apps.py`

Replace entire file with:
```python
from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class ReservationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reservations'

    def ready(self):
        """Initialize scheduler when Django starts"""
        try:
            from apscheduler.schedulers.background import BackgroundScheduler
            from .tasks import release_expired_locks
            
            scheduler = BackgroundScheduler()
            scheduler.add_job(
                release_expired_locks,
                trigger='interval',
                seconds=60,  # Run every 60 seconds
                id='release_expired_locks',
                name='Release expired seat locks'
            )
            
            if not scheduler.running:
                scheduler.start()
                logger.info("✅ Scheduler started: Locks released every 60s")
            
        except Exception as e:
            logger.error(f"❌ Scheduler error: {e}")
```

### Step 5: Test It

```bash
# Start Django server
python manage.py runserver

# Watch console output:
# ✅ Scheduler started: Locks released every 60s
# ✅ Auto-released 2 expired locks (after 60s)
```

### Result
- Automatic background cleanup
- No React changes needed
- Production-ready solution ✅
- 60-second interval (configurable)

---

## 📊 Comparison: Which Option to Choose?

```
┌──────────────┬────────────┬──────────────┬─────────────┐
│  Option      │  Effort    │  Frequency   │  Best For   │
├──────────────┼────────────┼──────────────┼─────────────┤
│ Manual Cmd   │ ⚡⚡ (done)  │ Manual        │ Testing     │
│ Option A (3s)│ ⚡⚡⚡ (5m)   │ Every 3s      │ Dev/Testing │
│ Option B (btn)│ ⚡⚡⚡ (15m) │ User clicks   │ Dashboard   │
│ Option C (60s)│ ⚡⚡⚡⚡ (20m)│ Every 60s     │ Production  │
└──────────────┴────────────┴──────────────┴─────────────┘
```

### Recommendation
- **Right now:** Use manual command ✅ (already done!)
- **This week:** Implement Option A or B
- **Production:** Use Option C

---

## ✅ Verification Checklist

After implementing:

- [ ] Run `python manage.py release_expired_locks` (test manual)
- [ ] Lock a seat and wait 5+ minutes
- [ ] Check if it's automatically released
- [ ] If using React: Lock seat → see it update in UI
- [ ] If using button: Click button → see locks release
- [ ] If using backend: Let it run → check console

---

## 🐛 Troubleshooting

### Command not found
```bash
# Make sure you're in the right directory
cd seat_reservation_workflow/seat_reservation

# Then try:
python manage.py release_expired_locks
```

### APScheduler not starting
```bash
# Check Django console for errors
# Make sure apps.py is properly configured
# Verify installed_apps has 'django_apscheduler'
```

### React not refreshing
```javascript
// Make sure interval is set
const interval = setInterval(fetchSeats, 3000);

// Make sure cleanup is called
return () => clearInterval(interval);
```

---

## 🎯 Final Checklist

- [x] Problem identified: Locks don't expire
- [x] Solution created: 3 options provided
- [x] Manual command ready: `release_expired_locks`
- [x] 19 locks released (test successful!)
- [ ] Choose your implementation (A, B, or C)
- [ ] Implement your choice
- [ ] Test thoroughly
- [ ] Deploy to production

---

**Pick an option above and implement it! Your choice determines auto-release behavior.** 🚀
