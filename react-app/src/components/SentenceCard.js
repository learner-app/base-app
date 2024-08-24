import React, { useState } from 'react';
import PropTypes from 'prop-types';
import RatingBar from './RatingBar';
import './SentenceCard.css';

const SentenceCard = ({ sentence, onSentenceUpdate }) => {
  const [userTranslation, setUserTranslation] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);

  if (!sentence) {
    return <div className="sentence-card error">No sentence data available</div>;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      const response = await fetch(`/sentences/${sentence.id}/translate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ translation: userTranslation }),
      });

      if (!response.ok) {
        throw new Error('Failed to submit translation');
      }

      const updatedSentence = await response.json();
      onSentenceUpdate(updatedSentence);
      setUserTranslation('');
    } catch (err) {
      setError(err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="sentence-card">
      <p>Sentence:</p>
      <p className="original-sentence">{sentence.sentence}</p>
      
      {sentence.user_translation ? (
        <div className="user-translation">
          <p>Your Translation: {sentence.user_translation}</p>
          <p>Our Translation: {sentence.machine_translation}</p>
          {sentence.evaluation_rating && (
            <div className="evaluation">
              <p>Quality:</p>
              <RatingBar rating={sentence.evaluation_rating} />
            </div>
          )}
          {sentence.evaluation_text && (
            <div>
                <p className="evaluation">Review:</p>
                <p className="review-text">{sentence.evaluation_text}</p>
            </div>
          )}
          {sentence.terms_used && (
            <div>
                <p className="evaluation">Terms Used:</p>
                <p className="review-text">{sentence.terms_used}</p>
            </div>
          )}
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="translation-form" autoComplete='off' autoCorrect='off' spellCheck='false'>
          <textarea
            value={userTranslation}
            onChange={(e) => setUserTranslation(e.target.value)}
            placeholder="Enter your translation here"
            required
            disabled={isSubmitting}
          />
          <button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Submitting...' : 'Submit Translation'}
          </button>
          {error && <p className="error-message">{error}</p>}
        </form>
      )}
    </div>
  );
};

SentenceCard.propTypes = {
  sentence: PropTypes.shape({
    id: PropTypes.number.isRequired,
    sentence: PropTypes.string.isRequired,
    user_translation: PropTypes.string,
    machine_translation: PropTypes.string,
    evaluation_rating: PropTypes.number,
    evaluation_text: PropTypes.string,
  }),
  onSentenceUpdate: PropTypes.func.isRequired,
};

export default SentenceCard;