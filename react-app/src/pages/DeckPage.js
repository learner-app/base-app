import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import NewTermButton from '../components/NewTermButton';
import TermCard from '../components/TermCard';
import CSVImportButton from '../components/CSVImportButton';
import './DeckPage.css';

export default function DeckPage() {
  const [deck, setDeck] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { deckId } = useParams();

  useEffect(() => {
    fetchDeck();
  }, [deckId]);

  const fetchDeck = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/decks/${deckId}/terms`);
      if (!response.ok) {
        throw new Error('Failed to fetch deck');
      }
      const data = await response.json();
      setDeck(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleNewTerm = (newTerm) => {
    setDeck(prevDeck => ({
      ...prevDeck,
      terms: [...prevDeck.terms, newTerm]
    }));
  };

  const handleEditTerm = async (termId, newTerm, newDefinition) => {
    try {
      const response = await fetch(`/terms/${termId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ term: newTerm, definition: newDefinition }),
      });

      if (!response.ok) {
        throw new Error('Failed to update term');
      }

      setDeck(prevDeck => ({
        ...prevDeck,
        terms: prevDeck.terms.map(term => 
          term.term_id === termId ? { ...term, term: newTerm, definition: newDefinition } : term
        )
      }));
    } catch (error) {
      console.error('Error updating term:', error);
    }
  };

  const handleDeleteTerm = async (termId) => {
    try {
      const response = await fetch(`/terms/${termId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to delete term');
      }

      setDeck(prevDeck => ({
        ...prevDeck,
        terms: prevDeck.terms.filter(term => term.term_id !== termId)
      }));
    } catch (error) {
      console.error('Error deleting term:', error);
    }
  };

  const handleImportSuccess = () => {
    fetchDeck();  // Refresh the deck data after successful import
  };

  if (loading) return <div className="loading">Loading deck...</div>;
  if (error) return <div className="error">Error: {error}</div>;
  if (!deck) return <div className="error">Deck not found</div>;

  return (
    <div className="deck-page">
      <Link to="/" className="back-button">← Back to Decks</Link>
      <h1 className="deck-title">{deck.deck_name}</h1>
      <p className="deck-info">
        {deck.deck_language + ' -> ' + deck.user_language + ' '} | 
        {' ' + deck.terms.length} terms | {deck.is_public ? 'Public' : 'Private'}
      </p>
      <div className="action-buttons">
        <NewTermButton deckId={deckId} onSubmit={handleNewTerm} />
        <CSVImportButton deckId={deckId} onImportSuccess={handleImportSuccess} />
        <Link to={`/deck/${deckId}/sentences`} className="action-button">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path>
          </svg>
          Sentence Mode
        </Link>
      </div>
      <div className="term-list-container">
        <div className="term-list-header">
          <span className="term-header">Term</span>
          <span className="definition-header">Definition</span>
        </div>
        <div className="term-list">
          {deck.terms.map((term) => (
            <TermCard 
              key={term.term_id} 
              term={term} 
              onEdit={handleEditTerm} 
              onDelete={handleDeleteTerm} 
            />
          ))}
        </div>
      </div>
    </div>
  );
}