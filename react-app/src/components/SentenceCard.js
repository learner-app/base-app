import React from 'react';
import PropTypes from 'prop-types';
import RatingBar from './RatingBar';
import './SentenceCard.css';

const SentenceCard = ({ sentence, onSentenceUpdate, showHint, onToggleHint }) => {
  const [userTranslation, setUserTranslation] = React.useState('');
  const [isSubmitting, setIsSubmitting] = React.useState(false);
  const [error, setError] = React.useState(null);

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

  const renderTermsUsed = (termsUsed) => {
    if (!termsUsed || Object.keys(termsUsed).length === 0) return null;

    return (
      <div>
        <p className="evaluation-text">Terms Used:</p>
        <ul className="terms-list">
          {Object.entries(termsUsed).map(([term, definition]) => (
            <li key={term}>
              <strong>{term}</strong>: {definition}
            </li>
          ))}
        </ul>
      </div>
    );
  };

  const renderNewTerms = (newTerms) => {
    if (!newTerms || Object.keys(newTerms).length === 0) return null;

    const termsList = Object.entries(newTerms).map(([term, definition]) => `${term}: ${definition}`).join(' | ');

    return (
      <div className="new-terms-hint">
        <p>{termsList}</p>
      </div>
    );
  };

  const hasNewTerms = sentence.new_terms && Object.keys(sentence.new_terms).length > 0;
  return (
    <div className="sentence-card">
      <p className="original-sentence">{sentence.sentence}</p>
      
      {sentence.user_translation ? (
        <div className="user-translation">
         <p className="translations-text"><strong>Your Translation:</strong> {sentence.user_translation}</p>
         <p className="translations-text"><strong>Our Translation:</strong> {sentence.machine_translation}</p>
          {sentence.evaluation_rating && sentence.evaluation_text && (
            <div>
                <p className="evaluation-text">Review:</p>
                <p className="review-text">{sentence.evaluation_text}</p>
                <RatingBar rating={sentence.evaluation_rating} />
            </div>
          )}
          {renderTermsUsed(sentence.terms_used)}
        </div>
      ) : (
        <>
          {hasNewTerms && (
            <button 
              className="hint-button" 
              onClick={onToggleHint}
            >
              {showHint ? "Hide hint" : "Don't know some terms?"}
            </button>
          )}
          {showHint && renderNewTerms(sentence.new_terms)}
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
        </>
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
    terms_used: PropTypes.object,
    new_terms: PropTypes.object,
  }),
  onSentenceUpdate: PropTypes.func.isRequired,
  showHint: PropTypes.bool.isRequired,
  onToggleHint: PropTypes.func.isRequired,
};

export default SentenceCard;