import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import DeckList from './pages/DeckList';
import DeckPage from './pages/DeckPage';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<DeckList />} />
          <Route path="/deck/:deckId" element={<DeckPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;