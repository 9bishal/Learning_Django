import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './UserReservations.css';

const API_BASE = 'http://localhost:8000';

function UserReservations({ onBack }) {
  const [reservations, setReservations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('');

  useEffect(() => {
    fetchReservations();
  }, []);

  const fetchReservations = async () => {
    try {
      const response = await axios.get(
        `${API_BASE}/api/reservations/`,
        { withCredentials: true }
      );
      if (response.data.success) {
        setReservations(response.data.reservations);
        setLoading(false);
      }
    } catch (error) {
      console.error('Error fetching reservations:', error);
      showMessage('Error loading reservations', 'error');
    }
  };

  const showMessage = (msg, type) => {
    setMessage(msg);
    setMessageType(type);
    setTimeout(() => setMessage(''), 3000);
  };

  const handleCancelReservation = async (reservationId) => {
    if (!window.confirm('Are you sure you want to cancel this reservation?')) {
      return;
    }

    try {
      const response = await axios.post(
        `${API_BASE}/api/reservations/${reservationId}/cancel/`,
        {},
        {
          withCredentials: true,
          headers: {
            'X-CSRFToken': getCookie('csrftoken'),
          }
        }
      );

      if (response.data.success) {
        showMessage('✅ Reservation cancelled successfully', 'success');
        fetchReservations();
      }
    } catch (error) {
      const errorMsg = error.response?.data?.error || 'Error cancelling reservation';
      showMessage('❌ ' + errorMsg, 'error');
    }
  };

  if (loading) {
    return (
      <div className="reservations-container">
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading reservations...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="reservations-container">
      <button className="back-button" onClick={onBack}>
        ← Back to Events
      </button>

      <div className="reservations-header">
        <h2>🎟️ My Reservations</h2>
        <p>View and manage your confirmed reservations</p>
      </div>

      {message && (
        <div className={`alert alert-${messageType}`}>
          {message}
        </div>
      )}

      {reservations.length === 0 ? (
        <div className="no-reservations">
          <p>📭 No reservations yet</p>
          <button className="create-btn" onClick={onBack}>
            🎫 Browse Events & Make a Reservation
          </button>
        </div>
      ) : (
        <div className="reservations-list">
          {reservations.map((reservation) => (
            <div key={reservation.id} className="reservation-card">
              <div className="reservation-header">
                <h3>{reservation.event_name}</h3>
                <span className={`status-badge status-${reservation.status}`}>
                  {reservation.status.toUpperCase()}
                </span>
              </div>

              <div className="reservation-details">
                <div className="detail-row">
                  <span className="label">🎫 Reservation ID:</span>
                  <span className="value">{reservation.id}</span>
                </div>

                <div className="detail-row">
                  <span className="label">🪑 Seats:</span>
                  <span className="value seats-list">
                    {reservation.seats.join(', ')}
                  </span>
                </div>

                <div className="detail-row">
                  <span className="label">💰 Total Price:</span>
                  <span className="value price">${reservation.total_price}</span>
                </div>

                <div className="detail-row">
                  <span className="label">📅 Booked On:</span>
                  <span className="value">
                    {new Date(reservation.created_at).toLocaleDateString('en-US', {
                      weekday: 'short',
                      year: 'numeric',
                      month: 'short',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </span>
                </div>
              </div>

              <button
                className="cancel-btn"
                onClick={() => handleCancelReservation(reservation.id)}
              >
                ❌ Cancel Reservation
              </button>
            </div>
          ))}
        </div>
      )}
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

export default UserReservations;
