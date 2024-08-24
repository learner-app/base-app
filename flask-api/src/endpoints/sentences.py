from flask import Blueprint, jsonify, request
from src import db
from src.models import Deck, GeneratedSentence, ArchivedSentence

sentences_bp = Blueprint("sentences", __name__)


@sentences_bp.route("/decks/<int:deck_id>/sentences", methods=["GET"])
def get_sentences(deck_id):
    deck = Deck.query.get_or_404(deck_id)
    sentences = GeneratedSentence.query.filter_by(deck_id=deck_id).all()

    print(sentences)

    return jsonify(
        {
            "sentences": [
                {
                    "id": sentence.id,
                    "sentence": sentence.sentence,
                    "machine_translation": sentence.machine_translation,
                    "user_translation": sentence.user_translation,
                    "evaluation_rating": sentence.evaluation_rating,
                    "evaluation_text": sentence.evaluation_text,
                    "created_at": sentence.created_at.isoformat(),
                }
                for sentence in sentences
            ]
        }
    )


@sentences_bp.route("/decks/<int:deck_id>/archive-sentences", methods=["POST"])
def archive_sentences(deck_id):
    deck = Deck.query.get_or_404(deck_id)
    sentences = GeneratedSentence.query.filter_by(deck_id=deck_id).all()

    for sentence in sentences:
        archived_sentence = ArchivedSentence(
            deck_id=sentence.deck_id,
            sentence=sentence.sentence,
            machine_translation=sentence.machine_translation,
            user_translation=sentence.user_translation,
            evaluation_rating=sentence.evaluation_rating,
            evaluation_text=sentence.evaluation_text,
        )
        db.session.add(archived_sentence)
        db.session.delete(sentence)

    db.session.commit()

    return (
        jsonify({"message": f"Archived {len(sentences)} sentences for deck {deck_id}"}),
        200,
    )
