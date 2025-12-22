# Understanding `select_for_update()` and Database Locking

## 📊 Visual Guide to Database Locking

### Without Locking (Race Condition) ❌

```
Timeline    User A                          User B
───────────────────────────────────────────────────────────

T0          SELECT Seat#1
            status = "available"

T1                                          SELECT Seat#1
                                            status = "available"

T2          UPDATE Seat#1
            status = "reserved"

T3                                          UPDATE Seat#1
                                            status = "reserved"
                                            
RESULT:     Both users think they reserved the same seat! 💥
```

**What happened:**
- Both transactions read "available" before anyone locked it
- Both updated the same row with "reserved"
- Database allowed both updates (no conflict detected)
- **Overbooking occurs!**

---

### With SELECT FOR UPDATE (Database Locking) ✅

```
Timeline    User A                          User B
───────────────────────────────────────────────────────────

T0          SELECT FOR UPDATE Seat#1
            ├─ Database acquires EXCLUSIVE LOCK
            │  (no other transaction can read/write)
            │
            └─ Successfully reads: status = "available"

T1                                          SELECT FOR UPDATE Seat#1
                                            ├─ WAITS...
                                            │  (trying to acquire lock)
                                            │  (User A still holds it)
                                            │
                                            └─ (blocked)

T2          UPDATE locked_until = now+5min
            UPDATE status = "locked"
            COMMIT
            └─ Lock released ✓

T3                                          ACQUIRES LOCK
                                            │
                                            └─ Reads: status = "locked"

T4                                          Checks: is_locked() = True
                                            
                                            Returns error:
                                            "Seat locked by another user"
                                            
                                            ROLLBACK

RESULT:     Only User A reserved the seat! ✓
            No overbooking! ✓
```

---

## 🔐 How the Lock Works

### Database Level

```
When you execute:
Seat.objects.select_for_update().get(id=1)

The database does:
1. LOCK TABLE seats IN EXCLUSIVE MODE (the specific row)
2. SELECT * FROM seats WHERE id = 1
3. Return the row to application

Why?
- LOCK is row-level (not whole table)
- EXCLUSIVE means: only this transaction can read/write
- Other transactions MUST WAIT for lock to be released
```

### In Django

```python
from django.db import transaction

# Start transaction
with transaction.atomic():
    # Request lock from database
    seat = Seat.objects.select_for_update().get(id=seat_id)
    
    # At this point:
    # - Database has locked the Seat row
    # - No other transaction can modify it
    # - We have guaranteed exclusive access
    
    # Safe to check and update
    if seat.status == 'available':
        seat.locked_until = timezone.now() + timedelta(seconds=300)
        seat.locked_by = current_user
        seat.status = 'locked'
        seat.save()
    
    # End transaction (COMMIT)
    # Lock automatically released!
```

---

## ⏰ The `locked_until` Field

### Purpose

`locked_until` stores when a **temporary hold** expires. It's a **timestamp**, not a boolean.

```python
class Seat(models.Model):
    locked_until = models.DateTimeField(null=True, blank=True)
    
    def is_locked(self):
        """Is this seat currently locked?"""
        if self.locked_until is None:
            return False  # Never been locked
        
        if timezone.now() < self.locked_until:
            return True   # Lock still active
        else:
            return False  # Lock expired
```

### Timeline Example

```
User locks Seat#1 at 10:00:00 UTC
│
├─ locked_until = "2025-12-21 10:05:00"
│
├─ Time: 10:00:05 → is_locked() = True ✓ (locked for 4m 55s)
├─ Time: 10:02:00 → is_locked() = True ✓ (locked for 2m 60s)
├─ Time: 10:04:59 → is_locked() = True ✓ (locked for 1 second)
├─ Time: 10:05:00 → is_locked() = False ✗ (exactly expired)
├─ Time: 10:05:01 → is_locked() = False ✗ (expired 1 second ago)
│
└─ Seat reverts to available automatically!
   (Next request will treat it as available)
```

---

## 🎬 Real-World Scenario: Movie Ticket Reservation

### Scenario: The Matrix - Seat A1 (Popular seat!)

```
10:00:00 → Alice's browser loads seats
           Seat A1 shows: status="available"

10:00:05 → Bob's browser loads seats
           Seat A1 shows: status="available"

10:00:10 → Alice clicks "Lock Seat A1"
           │
           ├─ POST /api/events/1/seats/1/lock/
           │  │
           │  └─ Backend:
           │     ├─ transaction.atomic() START
           │     ├─ SELECT FOR UPDATE Seat#1
           │     │  (database locks this row)
           │     ├─ Check: status == "available"? YES ✓
           │     ├─ locked_until = 10:05:10
           │     ├─ locked_by = "alice"
           │     ├─ status = "locked"
           │     ├─ COMMIT
           │     └─ (lock released)
           │
           └─ Response: "Seat A1 locked for 5 minutes" ✓

10:00:11 → Bob clicks "Lock Seat A1"
           │
           ├─ POST /api/events/1/seats/1/lock/
           │  │
           │  └─ Backend:
           │     ├─ transaction.atomic() START
           │     ├─ SELECT FOR UPDATE Seat#1
           │     │  (tries to acquire lock... WAITS)
           │     │  (Alice's lock not released yet!)
           │     │  
           │     │  [Alice's lock released at 10:00:10]
           │     │
           │     ├─ Finally acquires lock
           │     ├─ Check: status == "available"? NO ✗
           │     │  (status is "locked")
           │     ├─ Return error: "Seat locked by another user"
           │     └─ ROLLBACK
           │
           └─ Response: "❌ Seat locked by another user" ✗

10:00:15 → Alice's browser refreshes
           Seat A1 shows: status="locked" (locked by alice)
           Bob's browser shows: status="locked" (locked by alice)

10:04:00 → Alice confirms reservation
           │
           ├─ POST /api/events/1/reserve/
           │  │
           │  └─ Backend:
           │     ├─ SELECT FOR UPDATE Seats [1, ...]
           │     ├─ Verify all locked by alice? YES ✓
           │     ├─ Create Reservation
           │     ├─ For Seat#1:
           │     │  ├─ status = "reserved"
           │     │  ├─ reserved_by = "alice"
           │     │  ├─ Clear locked_until
           │     │  └─ Clear locked_by
           │     └─ COMMIT
           │
           └─ Response: "✓ Reservation confirmed" ✓

10:05:10 → Bob's lock would have expired, but...
           Alice already confirmed!
           Bob can't lock it anyway (status="reserved")

Result:    ✅ Alice got the ticket
           ❌ Bob didn't get it
           ✅ No double-booking!
```

---

## 🔧 How SELECT FOR UPDATE Works in Different Databases

### SQLite (Development)
```sql
SELECT * FROM reservations_seat 
WHERE id = 1 
LIMIT 1 
FOR UPDATE;

-- Acquires EXCLUSIVE lock on the row
```

### PostgreSQL (Production)
```sql
SELECT * FROM reservations_seat 
WHERE id = 1 
FOR UPDATE;

-- Acquires ROW-LEVEL EXCLUSIVE LOCK
-- Other transactions can read from other rows
-- Only blocks modifications to this specific row
```

### MySQL/MariaDB
```sql
SELECT * FROM reservations_seat 
WHERE id = 1 
FOR UPDATE;

-- Works similarly to PostgreSQL
-- Row-level locking
```

---

## 🚀 Performance Implications

### Lock Contention

```
High Traffic Scenario (100 users trying to lock Seat#1):

Without select_for_update():
├─ All 100 read the same data
├─ First 50 write successfully
└─ But next 50 users have stale data! ❌

With select_for_update():
├─ User #1 acquires lock
├─ Users #2-100 WAIT in queue
├─ User #1 completes in 50ms
├─ User #2 acquires lock (from queue)
├─ ...and so on
│
└─ Total time: 100 × 50ms = 5 seconds ✓
   (But all operations are safe and consistent)
```

### Best Practices

1. **Keep locked section SHORT**
   ```python
   # GOOD ✓
   with transaction.atomic():
       seat = Seat.objects.select_for_update().get(id=1)
       # Quick check and update (50ms)
       seat.locked_until = ...
       seat.save()
   
   # BAD ✗
   with transaction.atomic():
       seat = Seat.objects.select_for_update().get(id=1)
       time.sleep(5)  # BLOCKS other transactions!
       seat.save()
   ```

2. **Use select_for_update(skip_locked=True)** for non-blocking
   ```python
   # Return None if row is already locked (don't wait)
   seat = Seat.objects.select_for_update(skip_locked=True).first()
   ```

3. **Consider Redis** for even faster locking
   ```python
   # Redis is in-memory, faster than database
   # But requires additional infrastructure
   ```

---

## 📊 State Machine Diagram

```
                   ┌─────────────┐
                   │ AVAILABLE   │
                   │ (unlocked)  │
                   └──────┬──────┘
                          │
                    User clicks seat
                          │
                          ▼
                   ┌─────────────┐
                   │  LOCKED     │
        ┌─────────→│ (temp hold) │◄─────────┐
        │          │ locked_until│          │
        │          │ = now+5m    │          │
        │          └──────┬──────┘          │
        │                 │                  │
        │          ┌──────┴──────┐          │
        │          │             │          │
        │    User confirms    Lock expires  │
        │    reservation       (>5 min)     │
        │          │             │          │
        │          ▼             ▼          │
        │      ┌──────────┐ ┌─────────────┐│
        └──────│RESERVED  │ │ AVAILABLE   ││
               │(permanent)│ │(auto)       ││
               └──────────┘ └─────────────┘│
                   │                       │
            User cancels                   │
            reservation                    │
                   │                       │
                   └───────────────────────┘
```

---

## 🧠 Critical Differences

| Aspect | Without Lock | With `select_for_update()` |
|--------|--------------|---------------------------|
| **Race Conditions** | ❌ Possible | ✅ Impossible |
| **Data Consistency** | ❌ Can be stale | ✅ Always fresh |
| **Overbooking** | ❌ Can occur | ✅ Cannot occur |
| **Performance** | ✅ Very fast | ⚠️ Lock wait time |
| **Code Complexity** | ✅ Simple | ⚠️ More complex |
| **Production Ready** | ❌ No | ✅ Yes |

---

## 🎯 Key Takeaway

**`select_for_update()` acquires a database-level EXCLUSIVE LOCK on a row, preventing any other transaction from reading or writing that row until the lock is released.**

Combined with the `locked_until` timestamp, it creates a **foolproof system** for temporary seat holds that prevent overbooking while allowing other users to book other seats simultaneously.

---

**This is enterprise-grade database locking!** 🚀
