from src import db
from datetime import datetime


class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    # Relationship
    decks = db.relationship("Deck", back_populates="user", lazy="dynamic")

    def __repr__(self):
        return f"<User {self.username}>"


class Deck(db.Model):
    __tablename__ = "decks"

    deck_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    deck_name = db.Column(db.String, nullable=False)
    is_public = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    # Relationships
    user = db.relationship("User", back_populates="decks")
    terms = db.relationship("Term", back_populates="deck", lazy="dynamic")
    generated_sentences = db.relationship(
        "GeneratedSentence", back_populates="deck", lazy="dynamic"
    )
    archived_sentences = db.relationship(
        "ArchivedSentence", back_populates="deck", lazy="dynamic"
    )

    def __repr__(self):
        return f"<Deck {self.deck_name}>"


class Term(db.Model):
    __tablename__ = "terms"

    term_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    deck_id = db.Column(db.Integer, db.ForeignKey("decks.deck_id"), nullable=False)
    term = db.Column(db.String, nullable=False)
    definition = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    # Relationship
    deck = db.relationship("Deck", back_populates="terms")

    def __repr__(self):
        return f"<Term {self.term}>"


class GeneratedSentence(db.Model):
    __tablename__ = "generated_sentences"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    deck_id = db.Column(db.Integer, db.ForeignKey("decks.deck_id"), nullable=False)
    sentence = db.Column(db.Text, nullable=False)
    machine_translation = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    # Relationship
    deck = db.relationship("Deck", back_populates="generated_sentences")
    user_translations = db.relationship(
        "UserTranslation", back_populates="generated_sentence", lazy="dynamic"
    )

    def __repr__(self):
        return f"<GeneratedSentence {self.sentence[:20]}...>"


class UserTranslation(db.Model):
    __tablename__ = "user_translations"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    generated_sentence_id = db.Column(
        db.Integer, db.ForeignKey("generated_sentences.id"), nullable=False
    )
    user_translation = db.Column(db.Text)
    evaluation_result = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)

    # Relationship
    generated_sentence = db.relationship(
        "GeneratedSentence", back_populates="user_translations"
    )

    def __repr__(self):
        return f"<UserTranslation {self.user_translation[:20]}...>"


class ArchivedSentence(db.Model):
    __tablename__ = "archived_sentences"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    deck_id = db.Column(db.Integer, db.ForeignKey("decks.deck_id"), nullable=False)
    sentence = db.Column(db.Text, nullable=False)
    machine_translation = db.Column(db.Text, nullable=False)
    user_translation = db.Column(db.Text)
    evaluation_result = db.Column(db.Text)
    archived_at = db.Column(db.DateTime, default=datetime.now)

    # Relationships
    deck = db.relationship("Deck", back_populates="archived_sentences")

    def __repr__(self):
        return f"<ArchivedSentence {self.sentence[:20]}...>"
