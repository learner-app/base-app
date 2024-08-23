from flask import Blueprint, jsonify, request
from src import db
from src.models import Deck, Term
from anthropic import Anthropic
import os

prompts_bp = Blueprint("prompts", __name__)

# Initialize Anthropic client
anthropic = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


@prompts_bp.route("/decks/<int:deck_id>/generate_sentences", methods=["POST"])
def generate_sentences(deck_id):
    deck = Deck.query.get_or_404(deck_id)
    terms = Term.query.filter_by(deck_id=deck_id).all()

    if not terms:
        return jsonify({"error": "No terms found in this deck"}), 400

    # Prepare the prompt
    prompt = "Please create a sentence for each of the following terms, using their definitions. Here are the terms and definitions:\n\n"
    for term in terms:
        prompt += f"Term: {term.term}\nDefinition: {term.definition}\n\n"
    prompt += "Please provide a sentence for each term that demonstrates its usage based on the given definition."

    try:
        # Call Anthropic API
        message = anthropic.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1000,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt,
                        }
                    ],
                }
            ],
        )

        # Extract the generated sentences
        generated_text = message.content[0].text

        # Process the generated text to pair terms with sentences
        lines = generated_text.split("\n")
        results = []
        current_term = None
        current_sentence = ""
        for line in lines:
            if line.startswith("Term:"):
                if current_term:
                    results.append(
                        {"term": current_term, "sentence": current_sentence.strip()}
                    )
                current_term = line.split(":", 1)[1].strip()
                current_sentence = ""
            elif line.strip() and current_term:
                current_sentence += line + " "
        if current_term:
            results.append({"term": current_term, "sentence": current_sentence.strip()})

        return jsonify(
            {
                "deck_id": deck_id,
                "deck_name": deck.deck_name,
                "generated_sentences": results,
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500
