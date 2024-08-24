import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import SentenceCard from '../components/SentenceCard';
import GenerateSentencesButton from '../components/GenerateSentencesButton';
import './SentencePage.css';

export default function SentencePage() {
  const [sentences, setSentences] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState(null);
  const { deckId } = useParams();
  const navigate = useNavigate();

  useEffect(() => {
    fetchSentences();
  }, [deckId]);

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
  };

  const goToNext = () => {
    setCurrentIndex((prevIndex) => 
      prevIndex < sentences.length - 1 ? prevIndex + 1 : 0
    );
  };

  const handleGenerateSentences = async () => {
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
      const generateResponse = await fetch(`/decks/${deckId}/generate_sentences`, {
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
      fetchSentences();
    }
  };

  const allSentencesAnswered = sentences.every(sentence => sentence.user_translation);

  const goToReviewPage = () => {
    navigate(`/deck/${deckId}/review`);
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
          onClick={handleGenerateSentences} 
          isLoading={generating}
        />
        {allSentencesAnswered && (
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
    </div>
  );
}