from flask import Blueprint, jsonify, request
from src import db
from src.models import Term, Deck, User
from collections import defaultdict
import csv, io

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
        "user_language": deck.user_language,
        "study_language": deck.study_language,
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


@terms_bp.route("/decks/<int:deck_id>/import_terms", methods=["POST"])
def import_terms_from_csv(deck_id):
    # Check if the deck exists
    deck = Deck.query.get_or_404(deck_id)

    # Check if the request has the file part
    if "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files["file"]

    # If the user does not select a file, the browser submits an empty file without a filename
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    # Check if the file is a CSV
    if not file.filename.lower().endswith(".csv"):
        return jsonify({"error": "File must be a CSV"}), 400

    try:
        # Read the CSV file
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_reader = csv.reader(stream)

        # Skip the header row if it exists
        next(csv_reader, None)

        terms_added = 0
        for row in csv_reader:
            if (
                len(row) >= 2
            ):  # Ensure the row has at least two columns (term and definition)
                new_term = Term(deck_id=deck_id, term=row[0], definition=row[1])
                db.session.add(new_term)
                terms_added += 1

        db.session.commit()

        return (
            jsonify(
                {
                    "message": f"Successfully imported {terms_added} terms to deck {deck_id}",
                    "terms_added": terms_added,
                }
            ),
            201,
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
