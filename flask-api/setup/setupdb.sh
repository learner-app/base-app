#!/bin/bash

# Navigate to the parent directory
cd "$(dirname "$0")/.."

# Delete the existing database file if it exists
if [ -f "test_database.db" ]; then
    echo "Deleting existing test_database.db"
    rm test_database.db
fi

# Create a new database file and apply the schema
echo "Creating new test_database.db and applying schema"
sqlite3 test_database.db < setup/base_schema.sql

echo "Inserting default user into the database"
sqlite3 test_database.db <<EOF
INSERT INTO users (username, email) VALUES ('default_user', 'default_user@example.com');
EOF

# Get the user_id of the inserted user
USER_ID=$(sqlite3 test_database.db "SELECT user_id FROM users WHERE username='default_user';")

# Insert a deck for the default user
echo "Inserting default deck for the user"
sqlite3 test_database.db <<EOF
INSERT INTO decks (user_id, deck_name, user_language, deck_language, is_public) VALUES ($USER_ID, 'korean 1', 'English', 'Korean', 0);
EOF

# Get the deck_id of the inserted deck
DECK_ID=$(sqlite3 test_database.db "SELECT deck_id FROM decks WHERE deck_name='korean 1';")

# Insert sample terms into the terms table
echo "Inserting sample terms into the terms table"
sqlite3 test_database.db <<EOF
INSERT INTO terms (deck_id, term, definition) VALUES ($DECK_ID, '-(으)면 -(으)ㄹ수록', 'the more __, the more __');
INSERT INTO terms (deck_id, term, definition) VALUES ($DECK_ID, '사과', 'apple');
INSERT INTO terms (deck_id, term, definition) VALUES ($DECK_ID, '-(으)ㄹ 까요', 'should we _?');
INSERT INTO terms (deck_id, term, definition) VALUES ($DECK_ID, '영화', 'movie');
EOF

echo "Database setup complete"

# INSERT INTO terms (deck_id, term, definition) VALUES ($DECK_ID, '학생', 'student');
# INSERT INTO terms (deck_id, term, definition) VALUES ($DECK_ID, '편안', 'peace');
# INSERT INTO terms (deck_id, term, definition) VALUES ($DECK_ID, '느끼다', 'to feel');
# INSERT INTO terms (deck_id, term, definition) VALUES ($DECK_ID, '배고파다', 'to be hungry');
# INSERT INTO terms (deck_id, term, definition) VALUES ($DECK_ID, '계획', 'plan');
# INSERT INTO terms (deck_id, term, definition) VALUES ($DECK_ID, '노래방', 'noraebang / karaoke');
# INSERT INTO terms (deck_id, term, definition) VALUES ($DECK_ID, '받다', 'to receive, to get');