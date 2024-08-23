from flask import Blueprint, jsonify, request
from src import db
from src.models import Term, Deck, User
from collections import defaultdict

terms_bp = Blueprint("terms", __name__)


@terms_bp.route("/users/<int:user_id>/terms", methods=["GET"])
def get_terms_by_user(user_id):
    user = User.query.get_or_404(user_id)
    decks_with_terms = (
        Deck.query.filter(Deck.user_id == user_id).join(Term).add_entity(Term).all()
    )

    organized_terms = defaultdict(list)
    for deck, term in decks_with_terms:
        organized_terms[deck.deck_id].append(
            {
                "term_id": term.term_id,
                "term": term.term,
                "definition": term.definition,
                "created_at": term.created_at.isoformat(),
            }
        )

    response = {
        "user_id": user_id,
        "username": user.username,
        "decks": [
            {
                "deck_id": deck_id,
                "deck_name": Deck.query.get(deck_id).deck_name,
                "terms": terms,
            }
            for deck_id, terms in organized_terms.items()
        ],
    }

    return jsonify(response)


@terms_bp.route("/decks/<int:deck_id>/terms", methods=["GET"])
def get_terms_by_deck(deck_id):
    deck = Deck.query.get_or_404(deck_id)
    terms = Term.query.filter_by(deck_id=deck_id).all()

    response = {
        "deck_id": deck_id,
        "deck_name": deck.deck_name,
        "user_id": deck.user_id,
        "username": deck.user.username,
        "terms": [
            {
                "term_id": term.term_id,
                "term": term.term,
                "definition": term.definition,
                "created_at": term.created_at.isoformat(),
            }
            for term in terms
        ],
    }

    return jsonify(response)


@terms_bp.route("/terms/<int:term_id>", methods=["GET"])
def get_term(term_id):
    term = Term.query.get_or_404(term_id)
    return jsonify(
        {
            "term_id": term.term_id,
            "deck_id": term.deck_id,
            "term": term.term,
            "definition": term.definition,
            "created_at": term.created_at,
        }
    )


@terms_bp.route("/decks/<int:deck_id>/terms", methods=["POST"])
def create_term(deck_id):
    data = request.json
    new_term = Term(deck_id=deck_id, term=data["term"], definition=data["definition"])
    db.session.add(new_term)
    db.session.commit()
    return (
        jsonify(
            {
                "term_id": new_term.term_id,
                "deck_id": new_term.deck_id,
                "term": new_term.term,
                "definition": new_term.definition,
                "created_at": new_term.created_at,
            }
        ),
        201,
    )


@terms_bp.route("/terms/<int:term_id>", methods=["PUT"])
def update_term(term_id):
    term = Term.query.get_or_404(term_id)
    data = request.json

    if "term" in data:
        term.term = data["term"]
    if "definition" in data:
        term.definition = data["definition"]

    db.session.commit()

    return (
        jsonify(
            {
                "term_id": term.term_id,
                "deck_id": term.deck_id,
                "term": term.term,
                "definition": term.definition,
                "created_at": term.created_at.isoformat(),
            }
        ),
        200,
    )


@terms_bp.route("/terms/<int:term_id>", methods=["DELETE"])
def delete_term(term_id):
    term = Term.query.get_or_404(term_id)

    db.session.delete(term)
    db.session.commit()

    return jsonify({"message": f"Term {term_id} has been deleted"}), 200
