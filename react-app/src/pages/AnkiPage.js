import React, { useState, useEffect, useCallback } from 'react';
import { Heap } from 'heap-js';
import { useParams, Link } from 'react-router-dom';
import './AnkiPage.css';

const AnkiPage = () => {
  const { deckId } = useParams();
  const [deck, setDeck] = useState(null);
  const [currentCard, setCurrentCard] = useState(null);
  const [showAnswer, setShowAnswer] = useState(false);
  const [dueCount, setDueCount] = useState(0);
  const [cardHeap, setCardHeap] = useState(new Heap((a, b) => new Date(a.nextReview) - new Date(b.nextReview)));
  const [isStudyComplete, setIsStudyComplete] = useState(false);
  const [nextIntervals, setNextIntervals] = useState(null);

  const fetchDeckData = useCallback(async () => {
    try {
      const response = await fetch(`/decks/${deckId}/anki/initialize`, { method: 'POST' });
      const data = await response.json();
      setDeck(data.deck);
      setDueCount(data.progress.dueCount);
      data.cardQueue.forEach(card => cardHeap.push(card));
      showNextCard();
    } catch (error) {
      console.error('Error initializing deck:', error);
    }
  }, [deckId, cardHeap]);

  useEffect(() => {
    fetchDeckData();
  }, [fetchDeckData]);

  const showNextCard = () => {
    setDueCount(cardHeap.length);
    if (cardHeap.length > 0) {
        let nextCard = cardHeap.pop();

        setCurrentCard(nextCard);
        setShowAnswer(false);
        setIsStudyComplete(false);
        fetchNextIntervals(nextCard);
    } else {
        setCurrentCard(null);
        setIsStudyComplete(true);
    }
  };

  const fetchNextIntervals = async (card) => {
    try {
      const response = await fetch('/anki/next-intervals', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          interval: card.interval,
          easeFactor: card.easeFactor
        }),
      });
      const data = await response.json();
      setNextIntervals(data.nextIntervals);
    } catch (error) {
      console.error('Error fetching next intervals:', error);
    }
  };

  const handleShowAnswer = () => {
    setShowAnswer(true);
  };

  const handleRating = async (rating) => {
    try {
      const response = await fetch('/anki/rate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          term_id: currentCard.term_id,
          rating,
          interval: currentCard.interval,
          easeFactor: currentCard.easeFactor
        }),
      });
      const data = await response.json();
      console.log("data");
      console.log(data);
      
      const updatedCard = { ...currentCard, ...data };
      
      if (data.interval < 1) {
        cardHeap.push(updatedCard);
      }
      console.log(cardHeap);

      showNextCard();
    } catch (error) {
      console.error('Error rating card:', error);
    }
  };

  const handleReset = async () => {
    try {
      await fetch(`/decks/${deckId}/anki/reset`, { method: 'POST' });
      fetchDeckData();
      setCardHeap(new Heap((a, b) => new Date(a.nextReview) - new Date(b.nextReview)));
    } catch (error) {
      console.error('Error resetting deck:', error);
    }
  };

  if (!deck) return <div className="anki-deck__loading">Loading...</div>;

  return (
    <div className="anki-page">
      <Link className="back-button" to={`/deck/${deckId}`}>← Back to Deck</Link>
      <h1 className="anki-deck__title">{deck.deck_name}</h1>
      <div className="anki-deck__progress">
        Cards Due: {dueCount}
      </div>
      {isStudyComplete ? (
        <div className="anki-deck__complete">
          <p className="anki-deck__complete-message">Study complete! No more cards due at this time.</p>
          <button className="anki-deck__reset-button" onClick={handleReset}>Reset Deck</button>
        </div>
      ) : currentCard ? (
        <div className="anki-deck__card">
          <div className="anki-deck__term">{currentCard.term}</div>
          {showAnswer ? (
            <>
              <div className="anki-deck__definition">{currentCard.definition}</div>
              <div className="anki-deck__rating-buttons">
                {[1, 2, 3, 4].map(rating => (
                  <button 
                    key={rating}
                    className={`anki-deck__rating-button anki-deck__rating-button--${['again', 'hard', 'good', 'easy'][rating-1]}`}
                    onClick={() => handleRating(rating)}
                  >
                    {['Again', 'Hard', 'Good', 'Easy'][rating-1]}
                    {nextIntervals && (
                      <span className="anki-deck__next-interval">
                        {nextIntervals[rating].days < 1 
                          ? `${Math.round(nextIntervals[rating].days * 1440)} min` 
                          : `${nextIntervals[rating].days.toFixed(1)} days`}
                      </span>
                    )}
                  </button>
                ))}
              </div>
            </>
          ) : (
            <button className="anki-deck__show-answer-button" onClick={handleShowAnswer}>Show Answer</button>
          )}
        </div>
      ) : (
        <div className="anki-deck__no-cards">No cards to review at this time.</div>
      )}
    </div>
  );
};

export default AnkiPage;