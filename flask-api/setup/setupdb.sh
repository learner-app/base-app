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

echo "Database setup complete"