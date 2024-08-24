from flask import Blueprint, jsonify, request
from sqlalchemy import desc
from src import db
from src.models import Deck, User, Term

decks_bp = Blueprint("decks", __name__)


@decks_bp.route("/decks", methods=["GET"])
def get_decks():
    decks = Deck.query.all()
    return jsonify(
        [
            {
                "deck_id": deck.deck_id,
                "user_id": deck.user_id,
                "deck_name": deck.deck_name,
                "user_language": deck.user_language,
                "study_language": deck.study_language,
                "is_public": deck.is_public,
                "created_at": deck.created_at,
                "term_count": Term.query.filter_by(deck_id=deck.deck_id).count(),
            }
            for deck in decks
        ]
    )


@decks_bp.route("/users/<int:user_id>/decks", methods=["GET"])
def get_decks_by_user(user_id):
    user = User.query.get_or_404(user_id)
    decks = Deck.query.filter_by(user_id=user_id).order_by(desc(Deck.created_at)).all()
    return jsonify(
        {
            "user_id": user.user_id,
            "username": user.username,
            "decks": [
                {
                    "deck_id": deck.deck_id,
                    "deck_name": deck.deck_name,
                    "user_language": deck.user_language,
                    "study_language": deck.study_language,
                    "is_public": deck.is_public,
                    "created_at": deck.created_at.isoformat(),
                    "term_count": Term.query.filter_by(deck_id=deck.deck_id).count(),
                }
                for deck in decks
            ],
        }
    )


@decks_bp.route("/users/<int:user_id>/decks/oldest", methods=["GET"])
def get_decks_by_user_oldest_first(user_id):
    user = User.query.get_or_404(user_id)
    decks = Deck.query.filter_by(user_id=user_id).order_by(Deck.created_at).all()
    return jsonify(
        {
            "user_id": user.user_id,
            "username": user.username,
            "decks": [
                {
                    "deck_id": deck.deck_id,
                    "deck_name": deck.deck_name,
                    "user_language": deck.user_language,
                    "study_language": deck.study_language,
                    "is_public": deck.is_public,
                    "created_at": deck.created_at.isoformat(),
                    "term_count": Term.query.filter_by(deck_id=deck.deck_id).count(),
                }
                for deck in decks
            ],
        }
    )


@decks_bp.route("/decks/<int:deck_id>", methods=["GET"])
def get_deck(deck_id):
    deck = Deck.query.get_or_404(deck_id)
    return jsonify(
        {
            "deck_id": deck.deck_id,
            "user_id": deck.user_id,
            "deck_name": deck.deck_name,
            "user_language": deck.user_language,
            "study_language": deck.study_language,
            "is_public": deck.is_public,
            "created_at": deck.created_at,
            "term_count": Term.query.filter_by(deck_id=deck.deck_id).count(),
        }
    )


@decks_bp.route("/decks", methods=["POST"])
def create_deck():
    data = request.json
    new_deck = Deck(
        user_id=data["user_id"],
        deck_name=data["deck_name"],
        user_language=data["user_language"],
        study_language=data["study_language"],
        is_public=data.get("is_public", False),
    )
    db.session.add(new_deck)
    db.session.commit()
    return (
        jsonify(
            {
                "deck_id": new_deck.deck_id,
                "user_id": new_deck.user_id,
                "deck_name": new_deck.deck_name,
                "user_language": new_deck.user_language,
                "study_language": new_deck.study_language,
                "is_public": new_deck.is_public,
                "created_at": new_deck.created_at.isoformat(),
                "term_count": 0,
            }
        ),
        201,
    )


@decks_bp.route("/decks/<int:deck_id>", methods=["DELETE"])
def delete_deck(deck_id):
    deck = Deck.query.get_or_404(deck_id)

    # Delete associated terms
    Term.query.filter_by(deck_id=deck_id).delete()

    # Delete the deck
    db.session.delete(deck)
    db.session.commit()

    return jsonify({"message": f"Deck {deck_id} and its terms have been deleted"}), 200
