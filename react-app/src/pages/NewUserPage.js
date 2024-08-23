import React, { useState } from 'react';
import './NewUserPage.css';

export default function NewUserPage() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('/users', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, email }),
      });
      const data = await response.json();
      setMessage({ type: 'success', text: `User created with username: ${username}` });
    } catch (error) {
      setMessage({ type: 'error', text: 'Error creating user. Please try again.' });
    }
  };

  return (
    <div className="app-container">
      <div className="form-container">
        <h1 className="form-title">Create User</h1>
        <form onSubmit={handleSubmit} className="user-form">
          <div className="form-group">
            <label htmlFor="username" className="form-label">
              Username
            </label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="form-input"
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="email" className="form-label">
              Email
            </label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="form-input"
              required
            />
          </div>
          <button type="submit" className="submit-button">
            Create User
          </button>
        </form>
        {message && (
          <div className={`alert ${message.type === 'error' ? 'alert-error' : 'alert-success'}`}>
            <h4 className="alert-title">{message.type === 'error' ? 'Error' : 'Success'}</h4>
            <p className="alert-description">{message.text}</p>
          </div>
        )}
      </div>
    </div>
  );
}