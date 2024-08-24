import React from 'react';
import './GenerateSentencesButton.css';

const GenerateSentencesButton = ({ onClick, isLoading }) => {
  return (
    <button 
      onClick={onClick} 
      className="generate-sentences-button"
      disabled={isLoading}
    >
      {isLoading ? 'Generating...' : 'Generate New Sentences'}
    </button>
  );
};

export default GenerateSentencesButton;