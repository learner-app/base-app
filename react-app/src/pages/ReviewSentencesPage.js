import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import FinishedSentenceCard from '../components/CompletedSentenceCard';
import RatingBar from '../components/RatingBar';
import './ReviewSentencesPage.css';

export default function ReviewSentencesPage() {
  const [sentences, setSentences] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { deckId } = useParams();

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
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const calculateOverallPerformance = () => {
    const totalSentences = sentences.length;
    const totalRating = sentences.reduce((sum, sentence) => sum + (sentence.evaluation_rating || 0), 0);
    const averageRating = totalRating / totalSentences;
    return averageRating.toFixed(1);
  };

  if (loading) return <div className="loading">Loading review...</div>;
  if (error) return <div className="error">Error: {error}</div>;

  const overallPerformance = calculateOverallPerformance();

  return (
    <div className="review-sentences-page">
      <Link to={`/deck/${deckId}`} className="back-button">← Back to Deck</Link>
      <h1 className="page-title">Sentence Review</h1>
      
      <div className="overall-performance">
        <h2>Overall Performance</h2>
        <p>Average Rating: {overallPerformance}</p>
        <RatingBar rating={parseFloat(overallPerformance)} />
      </div>
      
      <div className="sentence-review-list">
        {sentences.map(sentence => (
          <FinishedSentenceCard key={sentence.id} sentence={sentence} />
        ))}
      </div>
    </div>
  );
}