from flask import Blueprint, jsonify, request
from src import db
from src.models import ReviewHistory, Term, UserTermData, Deck
from sqlalchemy import func
from datetime import datetime, timedelta, time

anki_bp = Blueprint("anki", __name__)


def calculate_next_interval(rating, current_interval, ease_factor):
    if rating < 1 or rating > 4:
        raise ValueError("Rating must be between 1 and 4")

    if rating == 1:
        return 1 / 1440  # 1 minute in days
    elif rating == 2:
        return 3 / 1440  # 10 minutes in days

    if current_interval < 10 / 1440:
        if rating == 3:
            return 15 / 1440
        elif rating == 4:
            return 3

    else:
        if rating == 3:
            next_interval = current_interval * ease_factor
            return next_interval if next_interval < 30 / 1440 else 1
        elif rating == 4:
            next_interval = current_interval * ease_factor * 1.5
            return next_interval if next_interval < 30 / 1440 else 1

    # This line should never be reached, but we'll return a default value just in case
    return max(current_interval, 1) * ease_factor


def get_next_review_date(interval):
    return datetime.now() + timedelta(days=interval)


def update_ease_factor(rating, current_ease_factor):
    if rating == 4:
        return min(current_ease_factor + 0.2, 2.5)
    elif rating == 3:
        return current_ease_factor
    elif rating == 2:
        return max(1.3, current_ease_factor - 0.15)
    else:  # rating == 1
        return max(1.3, current_ease_factor - 0.2)


def get_due_cards(user_id, deck_id):
    now = datetime.now()
    today = now.date()

    due_cards = (
        db.session.query(Term, UserTermData)
        .outerjoin(
            UserTermData,
            (Term.term_id == UserTermData.term_id) & (UserTermData.user_id == user_id),
        )
        .filter(Term.deck_id == deck_id)
        .filter(
            (func.date(UserTermData.next_review) <= today)
            | (UserTermData.next_review == None)
        )
        .order_by(func.coalesce(UserTermData.next_review, datetime.min))
        .all()
    )

    return [
        {
            "term_id": term.term_id,
            "term": term.term,
            "definition": term.definition,
            "nextReview": (
                user_term_data.next_review.isoformat()
                if user_term_data and user_term_data.next_review
                else datetime.combine(today, time.min).isoformat()
            ),
            "easeFactor": user_term_data.ease_factor if user_term_data else 2.5,
            "interval": user_term_data.interval if user_term_data else 0,
        }
        for term, user_term_data in due_cards
    ]


@anki_bp.route("/decks/<int:deck_id>/anki/initialize", methods=["POST"])
def initialize_anki_deck(deck_id):
    user_id = 1  # TODO: Replace with actual user authentication
    deck = Deck.query.get_or_404(deck_id)
    card_queue = get_due_cards(user_id, deck_id)
    total_cards = Term.query.filter_by(deck_id=deck_id).count()

    return jsonify(
        {
            "deck": {
                "deck_id": deck.deck_id,
                "deck_name": deck.deck_name,
            },
            "cardQueue": card_queue,
            "progress": {
                "reviewed": 0,
                "total": total_cards,
                "dueCount": len(card_queue),
            },
        }
    )


@anki_bp.route("/anki/rate", methods=["POST"])
def rate_anki_card():
    user_id = 1  # TODO: Replace with actual user authentication
    data = request.json

    user_term_data = UserTermData.query.filter_by(
        user_id=user_id, term_id=data["term_id"]
    ).first()
    if not user_term_data:
        user_term_data = UserTermData(user_id=user_id, term_id=data["term_id"])
        db.session.add(user_term_data)

    user_term_data.last_reviewed = datetime.now()
    user_term_data.interval = calculate_next_interval(
        data["rating"], data["interval"], data["easeFactor"]
    )
    user_term_data.ease_factor = update_ease_factor(data["rating"], data["easeFactor"])
    user_term_data.next_review = get_next_review_date(user_term_data.interval)

    review_history = ReviewHistory(
        user_id=user_id, term_id=data["term_id"], rating=data["rating"]
    )
    db.session.add(review_history)

    db.session.commit()

    return jsonify(
        {
            "nextReview": user_term_data.next_review.isoformat(),
            "easeFactor": user_term_data.ease_factor,
            "interval": user_term_data.interval,
        }
    )


@anki_bp.route("/decks/<int:deck_id>/anki/load-more-cards", methods=["GET"])
def load_more_cards(deck_id):
    user_id = 1  # TODO: Replace with actual user authentication

    card_queue = get_due_cards(user_id, deck_id)
    total_cards = Term.query.filter_by(deck_id=deck_id).count()
    reviewed_cards = (
        UserTermData.query.join(Term)
        .filter(
            Term.deck_id == deck_id,
            UserTermData.user_id == user_id,
            UserTermData.last_reviewed.isnot(None),
        )
        .count()
    )

    return jsonify(
        {
            "cardQueue": card_queue,
            "progress": {
                "reviewed": reviewed_cards,
                "total": total_cards,
                "dueCount": len(card_queue),
            },
        }
    )


@anki_bp.route("/decks/<int:deck_id>/anki/reset", methods=["POST"])
def reset_anki_progress(deck_id):
    user_id = 1  # TODO: Replace with actual user authentication

    try:
        # Delete UserTermData for this user and deck
        UserTermData.query.filter(
            UserTermData.user_id == user_id,
            UserTermData.term_id.in_(
                db.session.query(Term.term_id).filter_by(deck_id=deck_id)
            ),
        ).delete(synchronize_session=False)

        # Delete ReviewHistory for this user and deck
        ReviewHistory.query.filter(
            ReviewHistory.user_id == user_id,
            ReviewHistory.term_id.in_(
                db.session.query(Term.term_id).filter_by(deck_id=deck_id)
            ),
        ).delete(synchronize_session=False)

        db.session.commit()

        # Re-initialize the deck
        deck = Deck.query.get_or_404(deck_id)
        card_queue = get_due_cards(user_id, deck_id)
        total_cards = Term.query.filter_by(deck_id=deck_id).count()

        return jsonify(
            {
                "message": "Anki progress reset successfully",
                "deck": {
                    "deck_id": deck.deck_id,
                    "deck_name": deck.deck_name,
                },
                "cardQueue": card_queue,
                "progress": {
                    "reviewed": 0,
                    "total": total_cards,
                    "dueCount": len(card_queue),
                },
            }
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to reset progress: {str(e)}"}), 500


@anki_bp.route("/anki/next-intervals", methods=["POST"])
def get_next_intervals():
    data = request.json
    current_interval = data.get("interval", 0)
    current_ease_factor = data.get("easeFactor", 2.5)

    current_time = datetime.now()
    next_intervals = {}

    for rating in range(1, 5):
        next_interval = calculate_next_interval(
            rating, current_interval, current_ease_factor
        )
        next_review_date = current_time + timedelta(days=next_interval)
        next_intervals[rating] = {
            "days": next_interval,
            "date": next_review_date.isoformat(),
        }

    return jsonify({"nextIntervals": next_intervals})
