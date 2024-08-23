import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import './SentencePage.css';

export default function SentencePage() {
  const [sentences, setSentences] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { deckId } = useParams();

  useEffect(() => {
    generateSentences();
  }, [deckId]);

  const generateSentences = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`/decks/${deckId}/generate_sentences`, {
        method: 'POST',
      });
      if (!response.ok) {
        throw new Error('Failed to generate sentences');
      }
      const data = await response.json();
      setSentences(data.generated_sentences);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="loading">Generating sentences...</div>;
  if (error) return <div className="error">Error: {error}</div>;

  return (
    <div className="sentence-page">
      <Link to={`/deck/${deckId}`} className="back-button">← Back to Deck</Link>
      <h1 className="page-title">Generated Sentences</h1>
      {sentences.length === 0 ? (
        <p>No sentences generated yet.</p>
      ) : (
        <ul className="sentence-list">
          {sentences.map((sentence, index) => (
            <li key={index} className="sentence-item">
              <p><strong>Sentence:</strong> {sentence.sentence}</p>
              <p><strong>Translation:</strong> {sentence.translation}</p>
            </li>
          ))}
        </ul>
      )}
      <button onClick={generateSentences} className="generate-button">Generate New Sentences</button>
    </div>
  );
}
