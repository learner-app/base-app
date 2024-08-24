import React, { useState } from 'react';
import './NewDeckButton.css';

export default function NewDeckButton({ onSubmit }) {
  const [isOpen, setIsOpen] = useState(false);
  const [deckName, setDeckName] = useState('');
  const [isPublic, setIsPublic] = useState(false);
  const [userLanguage, setUserLanguage] = useState('English'); // default for now, TODO
  const [studyLanguage, setStudyLanguage] = useState('');

  const currentUserId = 1; // default

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('/decks', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: currentUserId,
          deck_name: deckName,
          is_public: isPublic,
          user_language: userLanguage,
          study_language: studyLanguage
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to create deck');
      }

      const data = await response.json();
      console.log('New deck created:', data);
      
      if (onSubmit) {
        onSubmit();
      }
      
      handleCancel();
    } catch (error) {
      console.error('Error creating deck:', error);
    }
  };

  const handleCancel = () => {
    setDeckName('');
    setIsPublic(false);
    setUserLanguage('');
    setStudyLanguage('');
    setIsOpen(false);
  };

  const handleModalClick = (e) => {
    e.stopPropagation();
  };

  return (
    <>
      <button className="new-deck-button" onClick={() => setIsOpen(true)}>
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="8" x2="12" y2="16"></line>
          <line x1="8" y1="12" x2="16" y2="12"></line>
        </svg>
        New Deck
      </button>
      {isOpen && (
        <div className="modal" onClick={handleCancel}>
          <div className="modal-content" onClick={handleModalClick}>
            <h2 className="modal-title">Create New Deck</h2>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label htmlFor="deck-name">Deck Name</label>
                <input
                  id="deck-name"
                  type="text"
                  value={deckName}
                  onChange={(e) => setDeckName(e.target.value)}
                  placeholder="Enter deck name"
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="user-language">Your Language</label>
                <input
                  id="user-language"
                  type="text"
                  value={userLanguage}
                  onChange={(e) => setUserLanguage(e.target.value)}
                  placeholder="Enter your language"
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="study-language">Study Language</label>
                <input
                  id="study-language"
                  type="text"
                  value={studyLanguage}
                  onChange={(e) => setStudyLanguage(e.target.value)}
                  placeholder="Enter language to study"
                  required
                />
              </div>
              <div className="checkbox-group">
                <input
                  type="checkbox"
                  id="is-public"
                  checked={isPublic}
                  onChange={(e) => setIsPublic(e.target.checked)}
                />
                <label htmlFor="is-public">Make deck public</label>
              </div>
              <div className="button-group">
                <button type="submit" className="submit-button">Create Deck</button>
                <button type="button" className="cancel-button" onClick={handleCancel}>Cancel</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}