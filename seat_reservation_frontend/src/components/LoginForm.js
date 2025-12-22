import React, { useState } from 'react';
import './LoginForm.css';

function LoginForm({ onLogin, loading }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (username.trim() && password.trim()) {
      onLogin(username, password);
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <div className="login-header">
          <h2>🎬 Seat Reservation</h2>
          <p>Sign in to your account</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter your username"
              disabled={loading}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <div className="password-input-wrapper">
              <input
                type={showPassword ? 'text' : 'password'}
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                disabled={loading}
                required
              />
              <button
                type="button"
                className="toggle-password"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? '🙈' : '👁️'}
              </button>
            </div>
          </div>

          <button
            type="submit"
            className="login-button"
            disabled={loading}
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <div className="demo-info">
          <h4>Demo Credentials:</h4>
          <p>Username: <code>admin</code></p>
          <p>Password: <code>admin123</code></p>
        </div>
      </div>

      <div className="login-features">
        <div className="feature">
          <span className="feature-icon">🎪</span>
          <h3>Browse Events</h3>
          <p>Explore upcoming movies, concerts, and conferences</p>
        </div>
        <div className="feature">
          <span className="feature-icon">🎯</span>
          <h3>Select Seats</h3>
          <p>Choose your favorite seats with real-time updates</p>
        </div>
        <div className="feature">
          <span className="feature-icon">🔒</span>
          <h3>Secure Reservation</h3>
          <p>Database-level locking prevents seat conflicts</p>
        </div>
      </div>
    </div>
  );
}

export default LoginForm;
