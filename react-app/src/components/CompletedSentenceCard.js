import React from 'react';
import PropTypes from 'prop-types';
import RatingBar from './RatingBar';
import './CompletedSentenceCard.css';

const CompletedSentenceCard = ({ sentence }) => {
  if (!sentence) {
    return <div className="finished-sentence-card error">No sentence data available</div>;
  }

  return (
    <div className="finished-sentence-card">
      <p className="label">Original Sentence:</p>
      <p className="original-sentence-fin">{sentence.sentence}</p>
      
      <p className="label">Your Translation:</p>
      <p className="user-translation-fin">{sentence.user_translation}</p>
      
      <p className="label">Our Translation:</p>
      <p className="machine-translation-fin">{sentence.machine_translation}</p>
      
      {sentence.evaluation_rating && (
        <div className="evaluation">
          <p className="label">Quality:</p>
          <RatingBar rating={sentence.evaluation_rating} />
        </div>
      )}
      
      {sentence.evaluation_text && (
        <div>
          <p className="label">Review:</p>
          <p className="review-text">{sentence.evaluation_text}</p>
        </div>
      )}
      
      {sentence.terms_used && (
        <div>
          <p className="label">Terms Used:</p>
          <p className="terms-used">{sentence.terms_used}</p>
        </div>
      )}
    </div>
  );
};

CompletedSentenceCard.propTypes = {
  sentence: PropTypes.shape({
    id: PropTypes.number.isRequired,
    sentence: PropTypes.string.isRequired,
    user_translation: PropTypes.string.isRequired,
    machine_translation: PropTypes.string.isRequired,
    evaluation_rating: PropTypes.number,
    evaluation_text: PropTypes.string,
    terms_used: PropTypes.string,
  }).isRequired,
};

export default CompletedSentenceCard;