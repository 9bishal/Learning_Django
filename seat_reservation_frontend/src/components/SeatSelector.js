import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './SeatSelector.css';

const API_BASE = 'http://localhost:8000';

function SeatSelector({ event, onBack, onReservationSuccess }) {
  const [seats, setSeats] = useState([]);
  const [selectedSeats, setSelectedSeats] = useState(new Set());
  const [loading, setLoading] = useState(true);
  const [reserving, setReserving] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState(''); // 'success', 'error', 'info'

  useEffect(() => {
    fetchSeats();
    // Poll for seat updates every 3 seconds to show real-time changes
    const interval = setInterval(fetchSeats, 3000);
    return () => clearInterval(interval);
  }, [event]);

  const fetchSeats = async () => {
    try {
      const response = await axios.get(
        `${API_BASE}/api/events/${event.id}/seats/`,
        { withCredentials: true }
      );
      if (response.data.success) {
        setSeats(response.data.seats);
        setLoading(false);
      }
    } catch (error) {
      console.error('Error fetching seats:', error);
      showMessage('Error fetching seats', 'error');
    }
  };

  const showMessage = (msg, type) => {
    setMessage(msg);
    setMessageType(type);
    setTimeout(() => setMessage(''), 3000);
  };

  const handleSeatClick = async (seat) => {
    if (seat.status === 'available' && !seat.is_locked) {
      // Lock the seat
      try {
        const response = await axios.post(
          `${API_BASE}/api/events/${event.id}/seats/${seat.id}/lock/`,
          {},
          {
            withCredentials: true,
            headers: {
              'X-CSRFToken': getCookie('csrftoken'),
            }
          }
        );

        if (response.data.success) {
          selectedSeats.add(seat.id);
          setSelectedSeats(new Set(selectedSeats));
          showMessage(`✅ Seat ${seat.seat_number} locked for 5 minutes`, 'success');
          fetchSeats();
        }
      } catch (error) {
        const errorMsg = error.response?.data?.error || 'Error locking seat';
        showMessage('❌ ' + errorMsg, 'error');
      }
    } else if (selectedSeats.has(seat.id)) {
      // Unlock the seat
      handleUnlockSeat(seat);
    }
  };

  const handleUnlockSeat = async (seat) => {
    try {
      const response = await axios.post(
        `${API_BASE}/api/events/${event.id}/seats/${seat.id}/unlock/`,
        {},
        {
          withCredentials: true,
          headers: {
            'X-CSRFToken': getCookie('csrftoken'),
          }
        }
      );

      if (response.data.success) {
        selectedSeats.delete(seat.id);
        setSelectedSeats(new Set(selectedSeats));
        showMessage(`🔓 Seat ${seat.seat_number} unlocked`, 'info');
        fetchSeats();
      }
    } catch (error) {
      showMessage('❌ Error unlocking seat', 'error');
    }
  };

  const handleReserve = async () => {
    if (selectedSeats.size === 0) {
      showMessage('Please select at least one seat', 'error');
      return;
    }

    setReserving(true);
    try {
      const response = await axios.post(
        `${API_BASE}/api/events/${event.id}/reserve/`,
        { seat_ids: Array.from(selectedSeats) },
        {
          withCredentials: true,
          headers: {
            'X-CSRFToken': getCookie('csrftoken'),
          }
        }
      );

      if (response.data.success) {
        showMessage(`✅ ${response.data.message}`, 'success');
        setTimeout(() => {
          onReservationSuccess();
        }, 1500);
      }
    } catch (error) {
      const errorMsg = error.response?.data?.error || 'Error reserving seats';
      showMessage('❌ ' + errorMsg, 'error');
      setReserving(false);
      fetchSeats();
    }
  };

  if (loading) {
    return (
      <div className="seat-selector">
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading seats...</p>
        </div>
      </div>
    );
  }

  const totalSeats = seats.length;
  const availableSeats = seats.filter(s => s.status === 'available').length;
  const reservedSeats = seats.filter(s => s.status === 'reserved').length;
  const lockedSeats = seats.filter(s => s.status === 'locked').length;

  return (
    <div className="seat-selector">
      <button className="back-button" onClick={onBack}>
        ← Back to Events
      </button>

      <div className="seat-selector-header">
        <h2>🎫 {event.name}</h2>
        <p>{event.location}</p>
      </div>

      {message && (
        <div className={`alert alert-${messageType}`}>
          {message}
        </div>
      )}

      <div className="seat-info">
        <div className="info-badge available">
          <span className="dot"></span>
          <span>Available: {availableSeats}</span>
        </div>
        <div className="info-badge locked">
          <span className="dot"></span>
          <span>Locked by Others: {lockedSeats}</span>
        </div>
        <div className="info-badge reserved">
          <span className="dot"></span>
          <span>Reserved: {reservedSeats}</span>
        </div>
        <div className="info-badge selected">
          <span className="dot"></span>
          <span>Selected by You: {selectedSeats.size}</span>
        </div>
      </div>

      <div className="screen">
        <p>🎬 SCREEN 🎬</p>
      </div>

      <div className="seats-grid">
        {seats.map((seat, index) => {
          const isSelected = selectedSeats.has(seat.id);

          return (
            <button
              key={seat.id}
              className={`seat ${seat.status} ${isSelected ? 'selected' : ''}`}
              onClick={() => handleSeatClick(seat)}
              disabled={
                seat.status === 'reserved' ||
                (seat.status === 'locked' && !isSelected)
              }
              title={`${seat.seat_number} - ${seat.status}${
                seat.is_locked ? ' (locked by others)' : ''
              }`}
            >
              <span className="seat-label">{seat.seat_number}</span>
            </button>
          );
        })}
      </div>

      <div className="seat-legend">
        <div className="legend-item">
          <div className="legend-color available"></div>
          <span>Available - Click to lock</span>
        </div>
        <div className="legend-item">
          <div className="legend-color selected"></div>
          <span>Selected by You - Click to unlock</span>
        </div>
        <div className="legend-item">
          <div className="legend-color locked"></div>
          <span>Locked by Others (expires in 5 min)</span>
        </div>
        <div className="legend-item">
          <div className="legend-color reserved"></div>
          <span>Already Reserved</span>
        </div>
      </div>

      <div className="selection-summary">
        <div className="summary-content">
          <h3>Selection Summary</h3>
          {selectedSeats.size > 0 ? (
            <>
              <p className="selected-count">
                Selected Seats: <strong>{selectedSeats.size}</strong>
              </p>
              <p className="selected-numbers">
                {seats
                  .filter(s => selectedSeats.has(s.id))
                  .map(s => s.seat_number)
                  .join(', ')}
              </p>
              <p className="price-info">
                Total Price: <strong>${selectedSeats.size * 100}</strong> (${100} per seat)
              </p>
            </>
          ) : (
            <p className="no-selection">No seats selected yet</p>
          )}
        </div>

        <div className="action-buttons">
          <button
            className="reserve-button"
            onClick={handleReserve}
            disabled={selectedSeats.size === 0 || reserving}
          >
            {reserving ? '⏳ Reserving...' : '✅ Confirm Reservation'}
          </button>
          <button
            className="cancel-button"
            onClick={onBack}
            disabled={reserving}
          >
            Cancel
          </button>
        </div>
      </div>

      <div className="info-box">
        <h4>⏱️ Lock Timeout Information</h4>
        <p>
          When you lock a seat, it is temporarily reserved for <strong>5 minutes</strong>. This gives you time to:
        </p>
        <ul>
          <li>Select multiple seats</li>
          <li>Review your selection</li>
          <li>Confirm your reservation</li>
        </ul>
        <p>
          <strong>Behind the scenes:</strong> Django uses <code>select_for_update()</code> with database-level
          locking to prevent race conditions. The <code>locked_until</code> field stores the lock expiration time.
        </p>
      </div>
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
