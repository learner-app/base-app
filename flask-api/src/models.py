from src import db
from datetime import datetime
import json


class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())

    # Relationships
    decks = db.relationship("Deck", back_populates="user", lazy="dynamic")
    user_term_data = db.relationship(
        "UserTermData", back_populates="user", lazy="dynamic"
    )
    review_history = db.relationship(
        "ReviewHistory", back_populates="user", lazy="dynamic"
    )

    def __repr__(self):
        return f"<User {self.username}>"


class Deck(db.Model):
    __tablename__ = "decks"

    deck_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    deck_name = db.Column(db.String, nullable=False)
    user_language = db.Column(db.String)
    deck_language = db.Column(db.String)
    is_public = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())

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
    created_at = db.Column(db.DateTime, default=datetime.now())

    # Relationships
    deck = db.relationship("Deck", back_populates="terms")
    user_term_data = db.relationship(
        "UserTermData", back_populates="term", lazy="dynamic"
    )
    review_history = db.relationship(
        "ReviewHistory", back_populates="term", lazy="dynamic"
    )

    def __repr__(self):
        return f"<Term {self.term}>"


class UserTermData(db.Model):
    __tablename__ = "user_term_data"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    term_id = db.Column(db.Integer, db.ForeignKey("terms.term_id"), nullable=False)
    last_reviewed = db.Column(db.DateTime)
    next_review = db.Column(db.DateTime)
    ease_factor = db.Column(db.Float, default=2.5)
    interval = db.Column(db.Integer, default=0)

    # Relationships
    user = db.relationship("User", back_populates="user_term_data")
    term = db.relationship("Term", back_populates="user_term_data")

    __table_args__ = (db.UniqueConstraint("user_id", "term_id", name="_user_term_uc"),)

    def __repr__(self):
        return f"<UserTermData user_id={self.user_id} term_id={self.term_id}>"


class ReviewHistory(db.Model):
    __tablename__ = "review_history"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    term_id = db.Column(db.Integer, db.ForeignKey("terms.term_id"), nullable=False)
    review_date = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    rating = db.Column(db.Integer, nullable=False)

    user = db.relationship("User", back_populates="review_history")
    term = db.relationship("Term", back_populates="review_history")

    def __repr__(self):
        return (
            f"<ReviewHistory {self.id} user_id={self.user_id} term_id={self.term_id}>"
        )


class GeneratedSentence(db.Model):
    __tablename__ = "generated_sentences"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    deck_id = db.Column(db.Integer, db.ForeignKey("decks.deck_id"), nullable=False)
    user_lang_given = db.Column(db.Boolean, nullable=False)
    sentence = db.Column(db.Text, nullable=False)
    machine_translation = db.Column(db.Text, nullable=False)
    terms_used_json = db.Column(db.Text, nullable=False, default="{}")
    new_terms_json = db.Column(db.Text, nullable=False, default="{}")
    user_translation = db.Column(db.Text)
    evaluation_rating = db.Column(db.Integer)
    evaluation_text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now())

    # Relationship
    deck = db.relationship("Deck", back_populates="generated_sentences")

    @property
    def terms_used(self):
        return json.loads(self.terms_used_json)

    @terms_used.setter
    def terms_used(self, value):
        self.terms_used_json = json.dumps(value)

    @property
    def new_terms(self):
        return json.loads(self.new_terms_json)

    @new_terms.setter
    def new_terms(self, value):
        self.new_terms_json = json.dumps(value)

    def __repr__(self):
        return f"<GeneratedSentence {self.sentence[:20]}...>"


class ArchivedSentence(db.Model):
    __tablename__ = "archived_sentences"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    deck_id = db.Column(db.Integer, db.ForeignKey("decks.deck_id"), nullable=False)
    user_lang_given = db.Column(db.Boolean, nullable=False)
    sentence = db.Column(db.Text, nullable=False)
    machine_translation = db.Column(db.Text, nullable=False)
    terms_used_json = db.Column(db.Text, nullable=False, default="{}")
    new_terms_json = db.Column(db.Text, nullable=False, default="{}")
    user_translation = db.Column(db.Text)
    evaluation_rating = db.Column(db.Integer)
    evaluation_text = db.Column(db.Text)
    archived_at = db.Column(db.DateTime, default=datetime.now())

    # Relationships
    deck = db.relationship("Deck", back_populates="archived_sentences")

    @property
    def terms_used(self):
        return json.loads(self.terms_used_json)

    @terms_used.setter
    def terms_used(self, value):
        self.terms_used_json = json.dumps(value)

    @property
    def new_terms(self):
        return json.loads(self.new_terms_json)

    @new_terms.setter
    def new_terms(self, value):
        self.new_terms_json = json.dumps(value)

    def __repr__(self):
        return f"<ArchivedSentence {self.sentence[:20]}...>"
