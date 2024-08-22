import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [currentTime, setCurrentTime] = useState(0);

  useEffect(() => {
    fetch('/api/time')
      .then(res => res.json())
      .then(data => {
        setCurrentTime(data.time);
      })
      .catch(err => console.error('Error fetching time:', err));
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        {/* ... no changes in this part ... */}
        <p>The current time is {currentTime}.</p>
      </header>
    </div>
  );
}

export default App;