import React, { useState, useEffect } from 'react';
import NewDeckButton from '../components/NewDeckButton';
import DeckCard from '../components/DeckCard';
import './DeckList.css';

export default function DeckList() {
  const [decks, setDecks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sortOldest, setSortOldest] = useState(false);
  const [deleteConfirmation, setDeleteConfirmation] = useState(null);
  const currentUserId = 1; // Default user ID

  useEffect(() => {
    fetchDecks();
  }, [sortOldest]);

  const fetchDecks = async () => {
    try {
      setLoading(true);
      const endpoint = sortOldest
        ? `/users/${currentUserId}/decks/oldest`
        : `/users/${currentUserId}/decks`;
      const response = await fetch(endpoint);
      if (!response.ok) {
        throw new Error('Failed to fetch decks');
      }
      const data = await response.json();
      setDecks(data.decks || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleNewDeck = () => {
    fetchDecks();
  };

  const toggleSort = () => {
    setSortOldest(!sortOldest);
  };

  const showDeleteConfirmation = (deck) => {
    setDeleteConfirmation(deck);
  };

  const handleDeleteDeck = async () => {
    if (!deleteConfirmation) return;

    try {
      const response = await fetch(`/decks/${deleteConfirmation.deck_id}`, {
        method: 'DELETE',
      });
      if (!response.ok) {
        throw new Error('Failed to delete deck');
      }
      setDecks(prevDecks => prevDecks.filter(deck => deck.deck_id !== deleteConfirmation.deck_id));
      setDeleteConfirmation(null);
    } catch (err) {
      setError(err.message);
    }
  };

  if (loading) return <div className="loading">Loading decks...</div>;
  if (error) return <div className="error">Error: {error}</div>;

  return (
    <div className="deck-list-container">
      <div className="deck-list-header">
        <h1 className="deck-list-title">My Decks</h1>
        <button onClick={toggleSort} className="sort-button">
          {sortOldest ? "Show Newest First" : "Show Oldest First"}
        </button>
      </div>
      <NewDeckButton onSubmit={handleNewDeck} />
      <ul className="deck-list">
        {decks.map(deck => (
          <DeckCard 
            key={deck.deck_id} 
            deck={deck} 
            onDeleteClick={showDeleteConfirmation} 
          />
        ))}
      </ul>

      {deleteConfirmation && (
        <div className="modal">
          <div className="modal-content">
            <h2>Confirm Deletion</h2>
            <p>Are you sure you want to delete the deck "{deleteConfirmation.deck_name}"?</p>
            <p>This action cannot be undone.</p>
            <div className="modal-buttons">
              <button onClick={handleDeleteDeck} className="confirm-delete">Delete</button>
              <button onClick={() => setDeleteConfirmation(null)} className="cancel-delete">Cancel</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}