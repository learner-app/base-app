import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import SentenceCard from '../components/SentenceCard';
import GenerateSentencesButton from '../components/GenerateSentencesButton';
import './SentencePage.css';

export default function SentencePage() {
  const [sentences, setSentences] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [showHint, setShowHint] = useState(false);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [userLangGiven, setUserLangGiven] = useState(false);
  const [sentenceCount, setSentenceCount] = useState('8');
  const [sentenceCountError, setSentenceCountError] = useState('');
  const [deckDetails, setDeckDetails] = useState(null);
  const { deckId } = useParams();
  const navigate = useNavigate();

  useEffect(() => {
    fetchDeckDetails();
    fetchSentences();
  }, [deckId]);

  const fetchDeckDetails = async () => {
    try {
      const response = await fetch(`/decks/${deckId}`);
      if (!response.ok) {
        throw new Error('Failed to fetch deck details');
      }
      const data = await response.json();
      setDeckDetails(data);
    } catch (err) {
      setError(err.message);
    }
  };

  const fetchSentences = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`/decks/${deckId}/sentences`);
      if (!response.ok) {
        throw new Error('Failed to fetch sentences');
      }
      const data = await response.json();
      setSentences(data.sentences);
      setCurrentIndex(findFirstUntranslatedIndex(data.sentences));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };


  const findFirstUntranslatedIndex = (sentences) => {
    const index = sentences.findIndex(sentence => !sentence.user_translation);
    return index !== -1 ? index : 0;
  };

  const handleSentenceUpdate = (updatedSentence) => {
    setSentences(prevSentences => 
      prevSentences.map(sentence => 
        sentence.id === updatedSentence.id ? { ...sentence, ...updatedSentence } : sentence
      )
    );
  };

  const goToPrevious = () => {
    setCurrentIndex((prevIndex) => 
      prevIndex > 0 ? prevIndex - 1 : sentences.length - 1
    );
    setShowHint(false);  // Reset hint when changing sentences
  };

  const goToNext = () => {
    setCurrentIndex((prevIndex) => 
      prevIndex < sentences.length - 1 ? prevIndex + 1 : 0
    );
    setShowHint(false);  // Reset hint when changing sentences
  };

  const handleToggleHint = () => {
    setShowHint(prevShowHint => !prevShowHint);
  };

  const handleSentenceCountChange = (e) => {
    const value = e.target.value;
    setSentenceCount(value);
    
    const numValue = parseInt(value, 10);
    if (isNaN(numValue) || numValue < 1) {
      setSentenceCountError('Minimum 0 sentences.');
    } else if (numValue > 12) {
      setSentenceCountError('Maximum 12 sentences.');
    } else {
      setSentenceCountError('');
    }
  };

  const handleGenerateSentences = async () => {
    if (sentenceCountError) {
      return;
    }
    setGenerating(true);
    setError(null);
    try {
      // First, archive existing sentences
      const archiveResponse = await fetch(`/decks/${deckId}/archive-sentences`, {
        method: 'POST',
      });
      if (!archiveResponse.ok) {
        throw new Error('Failed to archive existing sentences');
      }

      // Then, generate new sentences
      const generateResponse = await fetch(`/decks/${deckId}/generate_sentences?user_lang_given=${userLangGiven}&count=${sentenceCount}`, {
        method: 'POST',
      });
      if (!generateResponse.ok) {
        throw new Error('Failed to generate new sentences');
      }
      const data = await generateResponse.json();
      setSentences(data.generated_sentences || []);
      setCurrentIndex(0);
    } catch (err) {
      setError(err.message);
    } finally {
      setGenerating(false);
      setShowModal(false);
      fetchSentences();
    }
  };

  const allSentencesAnswered = sentences.every(sentence => sentence.user_translation);

  const goToReviewPage = () => {
    navigate(`/deck/${deckId}/review`);
  };

  const openGenerateModal = () => {
    setShowModal(true);
  };

  const closeGenerateModal = () => {
    setShowModal(false);
  };

  if (loading) return <div className="loading">Loading sentences...</div>;
  if (error) return <div className="error">Error: {error}</div>;

  const currentSentence = sentences[currentIndex];

  return (
    <div className="sentence-page">
      <Link to={`/deck/${deckId}`} className="back-button">← Back to Deck</Link>
      <h1 className="page-title">Sentence Practice</h1>
      
      <div className="sentence-button-container">
        <GenerateSentencesButton 
          onClick={openGenerateModal} 
          isLoading={generating}
        />
        {sentences.length > 0 && allSentencesAnswered && (
          <button onClick={goToReviewPage} className="review-page-button">
            Review Sentences
          </button>
        )}
      </div>
      
      {sentences.length === 0 ? (
        <div className="no-sentences-message">No sentences available. Click "Generate New Sentences" to create some!</div>
      ) : currentSentence ? (
        <div className="slideshow-container">
          <SentenceCard 
            sentence={currentSentence}
            onSentenceUpdate={handleSentenceUpdate}
            showHint={showHint}
            onToggleHint={handleToggleHint}
          />
          
          <div className="slideshow-controls">
            <button onClick={goToPrevious} className="nav-button prev">&#10094; Prev</button>
            <span className="sentence-count">
              {currentIndex + 1} / {sentences.length}
            </span>
            <button onClick={goToNext} className="nav-button next">Next &#10095;</button>
          </div>
        </div>
      ) : (
        <div className="error">No sentence found at current index. Try generating new sentences.</div>
      )}

      {showModal && deckDetails && (
        <div className="modal">
          <div className="modal-content">
            <h2>Generate New Sentences</h2>
            <div className="modal-options">
              <div className="language-direction">
                <label>
                  <input
                    type="radio"
                    name="languageDirection"
                    checked={!userLangGiven}
                    onChange={() => setUserLangGiven(false)}
                  />
                  {deckDetails.deck_language} → {deckDetails.user_language}
                </label>
                <label>
                  <input
                    type="radio"
                    name="languageDirection"
                    checked={userLangGiven}
                    onChange={() => setUserLangGiven(true)}
                  />
                  {deckDetails.user_language} → {deckDetails.deck_language}
                </label>
              </div>
              <div className="sentence-count">
                <label>
                  Number of sentences (1-12):
                  <input
                    type="text"
                    value={sentenceCount}
                    onChange={handleSentenceCountChange}
                  />
                </label>
              </div>
            </div>
            <div className="modal-buttons">
              <button 
                onClick={handleGenerateSentences} 
                disabled={generating || !!sentenceCountError}
                title={sentenceCountError || ''}
                className="generate-button"
              >
                {generating ? 'Generating...' : 'Generate'}
              </button>
              <button onClick={closeGenerateModal}>Cancel</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}