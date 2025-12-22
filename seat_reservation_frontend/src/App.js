import React, { useState, useEffect } from 'react';
import axios from 'axios';
import EventList from './components/EventList';
import SeatSelector from './components/SeatSelector';
import UserReservations from './components/UserReservations';
import LoginForm from './components/LoginForm';
import './App.css';

const API_BASE = 'http://localhost:8000';

function App() {
  const [currentView, setCurrentView] = useState('login'); // 'login', 'events', 'seats', 'reservations'
  const [events, setEvents] = useState([]);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(false);

  // Initialize axios with CSRF token
  useEffect(() => {
    const csrfToken = getCookie('csrftoken');
    axios.defaults.headers.common['X-CSRFToken'] = csrfToken;
    axios.defaults.withCredentials = true;
  }, []);

  // Check if user is logged in
  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/reservations/`);
      if (response.status === 200) {
        setIsLoggedIn(true);
        // Get current user from localStorage or API
        const user = localStorage.getItem('user');
        if (user) {
          setCurrentUser(JSON.parse(user));
        }
        setCurrentView('events');
        fetchEvents();
      }
    } catch (error) {
      setIsLoggedIn(false);
      setCurrentView('login');
    }
  };

  const handleLogin = async (username, password) => {
    setLoading(true);
    try {
      // Django's default login uses forms, so we'll use a custom approach
      // In production, you'd use Django's authentication endpoint
      const csrfToken = getCookie('csrftoken');
      const response = await axios.post(
        `${API_BASE}/api/login/`,
        { username, password },
        {
          headers: {
            'X-CSRFToken': csrfToken,
          }
        }
      );

      if (response.data.success) {
        setIsLoggedIn(true);
        setCurrentUser({ username, id: response.data.user_id });
        localStorage.setItem('user', JSON.stringify({ username, id: response.data.user_id }));
        setCurrentView('events');
        fetchEvents();
      }
    } catch (error) {
      console.error('Login failed:', error);
      alert('Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setCurrentUser(null);
    localStorage.removeItem('user');
    setCurrentView('login');
  };

  const fetchEvents = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/events/`);
      if (response.data.success) {
        setEvents(response.data.events);
      }
    } catch (error) {
      console.error('Error fetching events:', error);
    }
  };

  return (
    <div className="app">
      {isLoggedIn && (
        <header className="app-header">
          <div className="header-content">
            <h1>🎬 Seat Reservation System</h1>
            <div className="header-actions">
              <span className="user-info">Welcome, {currentUser?.username}!</span>
              <nav className="nav-buttons">
                <button
                  className={`nav-btn ${currentView === 'events' ? 'active' : ''}`}
                  onClick={() => setCurrentView('events')}
                >
                  🎪 Browse Events
                </button>
                <button
                  className={`nav-btn ${currentView === 'reservations' ? 'active' : ''}`}
                  onClick={() => setCurrentView('reservations')}
                >
                  🎟️ My Reservations
                </button>
                <button className="logout-btn" onClick={handleLogout}>
                  🚪 Logout
                </button>
              </nav>
            </div>
          </div>
        </header>
      )}

      <main className="app-main">
        {currentView === 'login' && (
          <LoginForm onLogin={handleLogin} loading={loading} />
        )}

        {currentView === 'events' && isLoggedIn && (
          <EventList
            events={events}
            onSelectEvent={(event) => {
              setSelectedEvent(event);
              setCurrentView('seats');
            }}
          />
        )}

        {currentView === 'seats' && isLoggedIn && selectedEvent && (
          <SeatSelector
            event={selectedEvent}
            onBack={() => {
              setCurrentView('events');
              setSelectedEvent(null);
            }}
            onReservationSuccess={() => {
              setCurrentView('reservations');
            }}
          />
        )}

        {currentView === 'reservations' && isLoggedIn && (
          <UserReservations onBack={() => setCurrentView('events')} />
        )}
      </main>
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

export default App;
