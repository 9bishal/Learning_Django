import React from 'react';
import './EventList.css';

function EventList({ events, onSelectEvent }) {
  const formatDate = (dateString) => {
    const options = {
      weekday: 'short',
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    };
    return new Date(dateString).toLocaleDateString('en-US', options);
  };

  const getAvailabilityPercentage = (event) => {
    return Math.round((event.available_seats / event.total_seats) * 100);
  };

  return (
    <div className="events-container">
      <div className="events-header">
        <h2>🎪 Upcoming Events</h2>
        <p>Browse and select from our exciting event collection</p>
      </div>

      {events.length === 0 ? (
        <div className="no-events">
          <p>📭 No events available at the moment</p>
        </div>
      ) : (
        <div className="events-grid">
          {events.map((event) => {
            const availabilityPercentage = getAvailabilityPercentage(event);

            return (
              <div key={event.id} className="event-card">
                <div className="event-poster">
                  <div className="poster-content">
                    <span className="event-icon">🎬</span>
                  </div>
                  <div className="availability-badge">
                    <span className="availability-text">
                      {event.available_seats}/{event.total_seats} seats
                    </span>
                  </div>
                </div>

                <div className="event-details">
                  <h3>{event.name}</h3>

                  <p className="description">{event.description}</p>

                  <div className="info-row">
                    <span className="info-label">📅 Date & Time:</span>
                    <span>{formatDate(event.event_date)}</span>
                  </div>

                  <div className="info-row">
                    <span className="info-label">📍 Location:</span>
                    <span>{event.location}</span>
                  </div>

                  <div className="availability-section">
                    <div className="availability-label">
                      <span>Availability: {availabilityPercentage}%</span>
                    </div>
                    <div className="availability-bar">
                      <div
                        className={`availability-fill ${
                          availabilityPercentage > 50 ? 'high' : 'low'
                        }`}
                        style={{
                          width: `${availabilityPercentage}%`
                        }}
                      />
                    </div>
                  </div>

                  <button
                    className="select-button"
                    onClick={() => onSelectEvent(event)}
                    disabled={event.available_seats === 0}
                  >
                    {event.available_seats === 0 ? '❌ Sold Out' : '🎫 Select Seats'}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default EventList;
