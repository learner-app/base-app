-- Users table
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Decks table
CREATE TABLE decks (
    deck_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    deck_name TEXT NOT NULL,
    is_public BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Terms table
CREATE TABLE terms (
    term_id INTEGER PRIMARY KEY AUTOINCREMENT,
    deck_id INTEGER NOT NULL,
    term TEXT NOT NULL,
    definition TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (deck_id) REFERENCES decks(deck_id)
);

-- GeneratedSentences table
CREATE TABLE generated_sentences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    deck_id INTEGER NOT NULL,
    sentence TEXT NOT NULL,
    machine_translation TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (deck_id) REFERENCES decks(deck_id)
);

-- UserTranslations table
CREATE TABLE user_translations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    generated_sentence_id INTEGER NOT NULL,
    user_translation TEXT,
    evaluation_result TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (generated_sentence_id) REFERENCES generated_sentences(id)
);

-- Indexes for faster lookups
CREATE INDEX idx_generated_sentence_deck ON generated_sentences(deck_id);
CREATE INDEX idx_user_translation_sentence ON user_translations(generated_sentence_id);
CREATE INDEX idx_deck_user ON decks(user_id);
CREATE INDEX idx_term_deck ON terms(deck_id);