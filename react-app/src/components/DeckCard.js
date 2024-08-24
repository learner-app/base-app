import React from 'react';
import { Link } from 'react-router-dom';
import './DeckCard.css';

const DeckCard = ({ deck, onDeleteClick }) => {
  return (
    <li className="deck-item">
      <div className="deck-content">
        <div className="deck-header">
          <h3 className="deck-name">
            <Link to={`/deck/${deck.deck_id}`}>{deck.deck_name}</Link>
          </h3>
          <button 
            onClick={() => onDeleteClick(deck)} 
            className="delete-button"
            aria-label="Delete deck"
          >
            🗑️
          </button>
        </div>
        <p className="deck-info">
          {deck.study_language + ' -> ' + deck.user_language + ' '} | 
          {' ' + deck.term_count} terms | 
          {deck.is_public ? ' Public' : ' Private'}
        </p>
      </div>
    </li>
  );
};

export default DeckCard;