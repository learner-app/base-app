import React, { useState } from 'react';
import './NewTermButton.css';

export default function NewTermButton({ deckId, onSubmit }) {
  const [isOpen, setIsOpen] = useState(false);
  const [term, setTerm] = useState('');
  const [definition, setDefinition] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`/decks/${deckId}/terms`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          term,
          definition
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to create term');
      }

      const data = await response.json();
      console.log('New term created:', data);
      
      if (onSubmit) {
        onSubmit(data);
      }
      
      setSuccessMessage('Term added successfully!');
      setTimeout(() => setSuccessMessage(''), 3000);  // Clear message after 3 seconds
      
      setTerm('');
      setDefinition('');
    } catch (error) {
      console.error('Error creating term:', error);
    }
  };

  const handleClose = () => {
    setTerm('');
    setDefinition('');
    setSuccessMessage('');
    setIsOpen(false);
  };

  return (
    <>
      <button className="new-term-button" onClick={() => setIsOpen(true)}>
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="8" x2="12" y2="16"></line>
          <line x1="8" y1="12" x2="16" y2="12"></line>
        </svg>
        New Term
      </button>
      {isOpen && (
        <div className="modal">
          <div className="modal-content">
            <h2 className="modal-title">Add New Term</h2>
            {successMessage && <div className="success-message">{successMessage}</div>}
            <form onSubmit={handleSubmit} autoComplete='off'>
              <div className="form-group">
                <label htmlFor="term">Term</label>
                <input
                  id="term"
                  type="text"
                  value={term}
                  onChange={(e) => setTerm(e.target.value)}
                  placeholder="Enter term"
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="definition">Definition</label>
                <textarea
                  id="definition"
                  value={definition}
                  onChange={(e) => setDefinition(e.target.value)}
                  placeholder="Enter definition"
                  required
                />
              </div>
              <div className="button-group">
                <button type="submit" className="submit-button">Add Term</button>
                <button type="button" className="close-button" onClick={handleClose}>Close</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}