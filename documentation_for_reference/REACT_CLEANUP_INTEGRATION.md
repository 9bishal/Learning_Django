# 🔄 Integrate Expired Lock Cleanup with React Frontend

## 🎯 The Problem We Fixed

Seats locked for 5 minutes weren't automatically becoming "available" after timeout.

## ✨ Solutions to Integrate with React

---

## 🟢 SOLUTION 1: Call Cleanup Before Fetching Seats (Simple)

### Concept
Before React displays seats, it refreshes the list. This triggers cleanup on the backend.

### Implementation

**File:** `src/components/SeatSelector.js`

```javascript
import { useEffect, useState } from 'react';
import axios from 'axios';

function SeatSelector({ eventId }) {
    const [seats, setSeats] = useState([]);
    const [loading, setLoading] = useState(false);

    // Add this effect - it runs when component loads
    useEffect(() => {
        fetchSeats();
        
        // Refresh seats every 3 seconds 
        const interval = setInterval(fetchSeats, 3000);
        
        return () => clearInterval(interval);
    }, [eventId]);

    // Updated fetch function
    const fetchSeats = async () => {
        try {
            setLoading(true);
            
            // Option A: Backend does cleanup automatically
            // Just fetch - if you set up APScheduler, it auto-cleans
            const response = await axios.get(
                `/api/events/${eventId}/seats/`,
                { withCredentials: true }
            );
            
            setSeats(response.data);
            
        } catch (error) {
            console.error('Error fetching seats:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="seat-selector">
            {loading && <p>Loading seats...</p>}
            {/* ... render seats ... */}
        </div>
    );
}

export default SeatSelector;
```

**How it works:**
1. React fetches seats every 3 seconds
2. Backend has APScheduler running (auto-cleanup every 60s)
3. Expired locks are released
4. Fresh seat list is returned to React
5. UI updates to show available seats

---

## 🟡 SOLUTION 2: Add a Cleanup Button (User Control)

### Concept
User can manually click a button to release expired locks.

### Implementation

**File:** `src/components/SeatSelector.js`

```javascript
import { useEffect, useState } from 'react';
import axios from 'axios';
import './SeatSelector.css';

function SeatSelector({ eventId }) {
    const [seats, setSeats] = useState([]);
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState('');

    useEffect(() => {
        fetchSeats();
    }, [eventId]);

    const fetchSeats = async () => {
        try {
            const response = await axios.get(
                `/api/events/${eventId}/seats/`,
                { withCredentials: true }
            );
            setSeats(response.data);
        } catch (error) {
            console.error('Error fetching seats:', error);
        }
    };

    // NEW: Release expired locks
    const releaseExpiredLocks = async () => {
        try {
            setLoading(true);
            setMessage('Releasing expired locks...');
            
            // Call Django API endpoint
            const response = await axios.post(
                '/api/release-expired-locks/',
                {},
                { 
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                    },
                    withCredentials: true 
                }
            );
            
            setMessage(`✅ ${response.data.count} locks released!`);
            
            // Refresh seat list
            await fetchSeats();
            
            // Clear message after 3 seconds
            setTimeout(() => setMessage(''), 3000);
            
        } catch (error) {
            setMessage('❌ Error releasing locks: ' + error.message);
        } finally {
            setLoading(false);
        }
    };

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

    return (
        <div className="seat-selector">
            <div className="seat-header">
                <h2>Select Your Seats</h2>
                {/* NEW: Add release button */}
                <button 
                    onClick={releaseExpiredLocks}
                    disabled={loading}
                    className="refresh-btn"
                    title="Release expired locks and refresh seat list"
                >
                    🔄 Refresh Availability
                </button>
            </div>

            {/* Show message */}
            {message && <p className="message">{message}</p>}

            {loading && <p>Loading...</p>}

            {/* Render seats */}
            <div className="seats-grid">
                {seats.map(seat => (
                    <div
                        key={seat.id}
                        className={`seat ${seat.status}`}
                        onClick={() => handleSeatClick(seat)}
                    >
                        {seat.seat_number}
                    </div>
                ))}
            </div>
        </div>
    );
}

export default SeatSelector;
```

**File:** `src/components/SeatSelector.css` (add styling)

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

.refresh-btn:hover:not(:disabled) {
    background-color: #45a049;
}

.refresh-btn:disabled {
    background-color: #cccccc;
    cursor: not-allowed;
}

.message {
    padding: 10px;
    margin: 10px 0;
    border-radius: 5px;
    background-color: #dff0d8;
    color: #3c763d;
    border: 1px solid #bce8f1;
}
```

### Add Django API Endpoint

**File:** `reservations/views.py` (add this view)

```python
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone
from .models import Seat
import json

@csrf_exempt
@require_http_methods(["POST"])
def release_expired_locks_api(request):
    """
    API endpoint to release expired locks
    Called from React frontend
    """
    try:
        now = timezone.now()
        
        # Find and release expired locks
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

**File:** `reservations/urls.py` (add URL)

```python
from django.urls import path
from . import views

urlpatterns = [
    # ... existing URLs ...
    
    # NEW: Add this line
    path('api/release-expired-locks/', views.release_expired_locks_api, name='release_expired_locks'),
]
```

---

## 🔵 SOLUTION 3: Auto-Cleanup Every 3 Seconds (React)

### Concept
React automatically triggers cleanup every time it refreshes seats.

### Implementation

**File:** `src/components/SeatSelector.js`

```javascript
import { useEffect, useState } from 'react';
import axios from 'axios';

function SeatSelector({ eventId }) {
    const [seats, setSeats] = useState([]);

    useEffect(() => {
        // Fetch seats immediately
        refreshSeats();
        
        // Then every 3 seconds: cleanup + fetch
        const interval = setInterval(refreshSeats, 3000);
        
        return () => clearInterval(interval);
    }, [eventId]);

    // Combined cleanup + fetch
    const refreshSeats = async () => {
        try {
            // Step 1: Release expired locks
            await axios.post(
                '/api/release-expired-locks/',
                {},
                { 
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                    },
                    withCredentials: true 
                }
            );
            
            // Step 2: Fetch fresh seat list
            const response = await axios.get(
                `/api/events/${eventId}/seats/`,
                { withCredentials: true }
            );
            
            setSeats(response.data);
            
        } catch (error) {
            console.error('Error refreshing seats:', error);
        }
    };

    return (
        <div className="seat-selector">
            {/* Render seats */}
            {seats.map(seat => (
                <div key={seat.id} className={`seat ${seat.status}`}>
                    {seat.seat_number}
                </div>
            ))}
        </div>
    );
}

export default SeatSelector;
```

**Timeline:**
```
T=0s:    React loads, calls refreshSeats()
         → Release expired locks
         → Fetch fresh seats
         
T=3s:    Timer fires, calls refreshSeats()
         → Release expired locks
         → Fetch fresh seats
         
T=6s:    Timer fires again...
         
T=305s:  User's lock expired
         → Next refreshSeats() (at T=306s) releases it
         → Seats show as available
```

---

## 🟣 SOLUTION 4: Set Up Auto-Release Backend (Best)

### Concept
Backend automatically releases locks every 60 seconds using APScheduler.
React doesn't need to do anything!

### Implementation

See `AUTO_RELEASE_EXPIRED_LOCKS.md` for full setup.

**Summary:**
```bash
pip install django-apscheduler

# Add to settings.py + create tasks.py
# Then:
python manage.py runserver

# Locks auto-release every 60 seconds
# React just fetches normally
```

**React code (no changes needed):**
```javascript
// Same as always
useEffect(() => {
    fetchSeats();
}, []);

const fetchSeats = async () => {
    const response = await axios.get(`/api/events/${eventId}/seats/`);
    setSeats(response.data);  // Always gets fresh data
};
```

---

## 📊 Comparison of Solutions

| Solution | Effort | How Often | Best For |
|----------|--------|-----------|----------|
| **1: Auto-Fetch** | Easy | Every 3s | Development |
| **2: Manual Button** | Medium | User clicks | User control |
| **3: Auto-Every-3s** | Medium | Every 3s | Small apps |
| **4: APScheduler Backend** | Hard | Every 60s | Production |

---

## ✅ Recommended Setup (Balanced)

### For Development/Testing:
```javascript
// Solution 1: Just refresh seats every 3 seconds
useEffect(() => {
    const interval = setInterval(fetchSeats, 3000);
    return () => clearInterval(interval);
}, []);
```

### For Production:
```bash
# Set up APScheduler (Solution 4)
pip install django-apscheduler
# Follow AUTO_RELEASE_EXPIRED_LOCKS.md

# React stays simple
useEffect(() => {
    fetchSeats();
}, []);
```

---

## 🧪 Test It Out

### Step 1: Lock a Seat
- Open React app
- Lock a seat (note the time)
- Check database: `locked_until` is 5 minutes from now

### Step 2: Wait 5 Minutes

### Step 3: Check What Happens

**Without Solution:** Seat still locked ❌

**With Solution:** Seat automatically released ✅
- Manual: Run `python manage.py release_expired_locks`
- Button: Click "Refresh Availability" 
- Auto: Happens automatically

---

## 🎯 Summary

| Need | Solution |
|------|----------|
| Quick fix for testing | Solution 1 or 2 |
| User control | Solution 2 (button) |
| Automatic (dev) | Solution 3 (every 3s) |
| Automatic (prod) | Solution 4 (APScheduler) |
| Manual cleanup | `python manage.py release_expired_locks` |

Pick one and enjoy automatic seat lock expiration! 🎉
