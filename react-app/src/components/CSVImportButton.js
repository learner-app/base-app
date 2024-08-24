import React, { useState } from 'react';
import './CSVImportButton.css';

const CSVImportButton = ({ deckId, onImportSuccess }) => {
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (file) {
      setIsUploading(true);
      setError(null);

      const formData = new FormData();
      formData.append('file', file);

      try {
        const response = await fetch(`/decks/${deckId}/import_terms`, {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          throw new Error('Failed to import CSV');
        }

        const result = await response.json();
        console.log('CSV import successful:', result);
        onImportSuccess();
      } catch (err) {
        setError(err.message);
      } finally {
        setIsUploading(false);
      }
    }
  };

  return (
    <div className="csv-import-container">
      <label className="action-button">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
          <polyline points="17 8 12 3 7 8"></polyline>
          <line x1="12" y1="3" x2="12" y2="15"></line>
        </svg>
        {isUploading ? 'Uploading...' : 'Import CSV'}
        <input
          type="file"
          accept=".csv"
          onChange={handleFileUpload}
          style={{ display: 'none' }}
          disabled={isUploading}
        />
      </label>
      {error && <p className="csv-import-error">{error}</p>}
    </div>
  );
};

export default CSVImportButton;