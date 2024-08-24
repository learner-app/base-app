import React, { useState } from 'react';
import './TermCard.css';

export default function TermCard({ term, onEdit, onDelete }) {
  const [isEditing, setIsEditing] = useState(false);
  const [editedTerm, setEditedTerm] = useState(term.term);
  const [editedDefinition, setEditedDefinition] = useState(term.definition);

  const handleEdit = () => {
    onEdit(term.term_id, editedTerm, editedDefinition);
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditedTerm(term.term);
    setEditedDefinition(term.definition);
    setIsEditing(false);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleEdit();
    }
  };

  return (
    <div className="term-card">
      {isEditing ? (
        <>
          <input
            value={editedTerm}
            onChange={(e) => setEditedTerm(e.target.value)}
            onKeyDown={handleKeyDown}
            className="term-input"
            placeholder="Term"
          />
          <input
            value={editedDefinition}
            onChange={(e) => setEditedDefinition(e.target.value)}
            onKeyDown={handleKeyDown}
            className="definition-input"
            placeholder="Definition"
          />
          <div className="term-actions">
            <button onClick={handleEdit} className="icon-button save-button" title="Save">
              ✓
            </button>
            <button onClick={handleCancel} className="icon-button cancel-button" title="Cancel">
              ✕
            </button>
          </div>
        </>
      ) : (
        <>
          <span className="term" title={term.term}>{term.term}</span>
          <div className="definition-container">
            <span className="definition" title={term.definition}>{term.definition}</span>
            <div className="term-actions">
              <button onClick={() => setIsEditing(true)} className="icon-button edit-button" title="Edit">
                ✎
              </button>
              <button onClick={() => onDelete(term.term_id)} className="icon-button delete-button" title="Delete">
                🗑️
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}