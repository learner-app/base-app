from flask import Blueprint, jsonify, request
from src import db
from src.models import Deck, GeneratedSentence, Term
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
    prompt = "Here is a list of terms and their definitions."
    for term in terms:
        prompt += f"Term: {term.term}\nDefinition: {term.definition}\n\n"
    prompt += "Please create 6 example coherent and meaningful sentences that demonstrate the usage of the given terms, according to their corresponding definitions.\n"
    prompt += "Please refrain from using complicated vocabulary and grammar that is not inside the list of terms. It is okay to assume very basic knowledge of vocabulary and grammar of the language."
    prompt += "If there are grammatical terms (such as tense & phrases) in the list, use them slightly more often than other vocabulary."
    prompt += "Ensure that the sentences generated make logical sense and are actually useful for everyday conversation or scenarios."
    prompt += "Your goal is to map these sentences to their translations in English in the following format:\n"
    prompt += (
        "Sentence: {example sentence}\nTranslation: {corresponding translation}\n\n"
    )
    prompt += "ONLY PROVIDE the sentences and translations strictly in the above format and NOTHING ELSE."

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

        sentences = []
        for entry in generated_text.split("\n\n"):
            if "Sentence:" in entry and "Translation:" in entry:
                sentence = entry.split("Sentence:")[1].split("Translation:")[0].strip()
                translation = entry.split("Translation:")[1].strip()
                sentences.append({"sentence": sentence, "translation": translation})

        for sentence in sentences:
            new_sentence = GeneratedSentence(
                deck_id=deck_id,
                sentence=sentence["sentence"],
                machine_translation=sentence["translation"],
            )
            db.session.add(new_sentence)
            db.session.commit()

        returnJson = jsonify(
            {
                "deck_id": deck_id,
                "deck_name": deck.deck_name,
                "generated_sentences": sentences,
            }
        )

        return returnJson

    except Exception as e:
        return jsonify({"error": str(e)}), 500
