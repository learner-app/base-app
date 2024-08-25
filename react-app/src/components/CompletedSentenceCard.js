import React from 'react';
import PropTypes from 'prop-types';
import RatingBar from './RatingBar';
import './CompletedSentenceCard.css';

const CompletedSentenceCard = ({ sentence }) => {
  if (!sentence) {
    return <div className="finished-sentence-card error">No sentence data available</div>;
  }

  const renderTermsUsed = (termsUsed) => {
    if (!termsUsed || Object.keys(termsUsed).length === 0) return null;

    return (
      <ul className="terms-used-fin">
        {Object.entries(termsUsed).map(([term, definition]) => (
          <li key={term}>
            {term}: {definition}
          </li>
        ))}
      </ul>
    );
  };

  const renderNewTerms = (newTerms) => {
    if (!newTerms || Object.keys(newTerms).length === 0) return null;

    const termsList = Object.entries(newTerms).map(([term, definition]) => `${term}: ${definition}`).join(' | ');

    return (
      <div>
        <p className="label-fin">New Terms:</p>
        <div className="new-terms-hint">
            <p>{termsList}</p>
        </div>
      </div>
    );
  };

  return (
    <div className="finished-sentence-card">
      <p className="label-fin">Original Sentence:</p>
      <p className="original-sentence-fin">{sentence.sentence}</p>
      
      <p className="label-fin">Your Translation:</p>
      <p className="user-translation-fin">{sentence.user_translation}</p>
      
      <p className="label-fin">Our Translation:</p>
      <p className="machine-translation-fin">{sentence.machine_translation}</p>
      
      {sentence.evaluation_rating && sentence.evaluation_text && (
        <div className="evaluation-fin">
          <p className="label-fin">Review:</p>
          <p className="review-text-fin">{sentence.evaluation_text}</p>
          <RatingBar rating={sentence.evaluation_rating} />
        </div>
      )}
      
      {sentence.terms_used && (
        <div>
          <p className="label-fin">Terms Used:</p>
          {renderTermsUsed(sentence.terms_used)}
        </div>
      )}

      {sentence.new_terms && (
        <div>
          {renderNewTerms(sentence.new_terms)}
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
    terms_used: PropTypes.object,
    new_terms: PropTypes.object,
    evaluation_rating: PropTypes.number,
    evaluation_text: PropTypes.string,
  }).isRequired,
};

export default CompletedSentenceCard;