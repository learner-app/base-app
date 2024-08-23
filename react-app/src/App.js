import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import DeckList from './pages/DeckList';
import DeckPage from './pages/DeckPage';
import SentencePage from './pages/SentencePage';
import NewUserPage from './pages/NewUserPage';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<DeckList />} />
          <Route path="/new-user" element={<NewUserPage />} />
          <Route path="/deck/:deckId" element={<DeckPage />} />
          <Route path="/deck/:deckId/sentences" element={<SentencePage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;