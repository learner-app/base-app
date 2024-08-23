import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import NewTermButton from '../components/NewTermButton';
import TermCard from '../components/TermCard';
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

  if (loading) return <div className="loading">Loading deck...</div>;
  if (error) return <div className="error">Error: {error}</div>;
  if (!deck) return <div className="error">Deck not found</div>;

  return (
    <div className="deck-page">
      <Link to="/" className="back-button">← Back to Decks</Link>
      <Link to={`/deck/${deckId}/sentences`} className="generate-sentences-link">Generate Sentences</Link>
      <h1 className="deck-title">{deck.deck_name}</h1>
      <p className="deck-info">
        {deck.terms.length} terms | {deck.is_public ? 'Public' : 'Private'}
      </p>
      <div className="new-term-container">
        <NewTermButton deckId={deckId} onSubmit={handleNewTerm} />
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
  );
}