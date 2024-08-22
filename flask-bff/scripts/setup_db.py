import sqlite3

connection = sqlite3.connect("../test_database.db")

with open("base_schema.sql") as f:
    connection.executescript(f.read())

connection.commit()
connection.close()
