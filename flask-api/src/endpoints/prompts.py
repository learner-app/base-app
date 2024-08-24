from flask import Blueprint, jsonify, request
from src import db
from src.models import Deck, GeneratedSentence, Term
from anthropic import Anthropic
import os, re, random

prompts_bp = Blueprint("prompts", __name__)

# Initialize Anthropic client
anthropic = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


@prompts_bp.route("/decks/<int:deck_id>/generate_sentences", methods=["POST"])
def generate_sentences(deck_id):
    deck = Deck.query.get_or_404(deck_id)
    terms = Term.query.filter_by(deck_id=deck_id).all()

    if not terms:
        return jsonify({"error": "No terms found in this deck"}), 400

    # Shuffle the terms for randomness
    random.shuffle(terms)

    terms_list = "\n".join(
        f"Term: {term.term}\nDefinition: {term.definition}" for term in terms
    )

    # First pass: Generate 10 sentences
    first_pass_prompt = f"""You are an expert language tutor creating practice sentences for a student learning {deck.study_language}. Their native language is {deck.user_language}.
    Here is a list of terms and their definitions that the student is learning.

    {terms_list}

    Your task is to create 10 example {deck.study_language} sentences and their {deck.user_language} translations that demonstrate the usage of these terms. Follow these guidelines:

    1. Create coherent, meaningful sentences that accurately use the terms according to their definitions. Ensure you use the terms themselves, and not synonyms or alternate language.
    2. Use simple language and refrain from using vocabulary or grammar that is not in the term list. However, you may use common words and grammar structures known to beginners, and you may use adjacent vocabulary if they help demonstrate the meaning of the terms.
    3. Ensure both the {deck.study_language} sentences and their {deck.user_language} translations are completely grammatically sound.
    4. Ensure that these sentences are natural and suitable for everyday conversations and practical scenarios.

    Present your examples in this format:
    Sentence: {{example sentence in {deck.study_language}}}
    Translation: {{corresponding translation in {deck.user_language}}}

    Provide ONLY the examples in the specified format, with no additional commentary."""

    # TODO: should we make the LLM also return the terms used in each sentence? for better quality of review later

    try:
        first_pass_message = anthropic.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1000,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": first_pass_prompt,
                        }
                    ],
                }
            ],
        )

        # Extract and process the generated sentences
        first_pass_text = first_pass_message.content[0].text

        sentences = []
        for entry in first_pass_text.split("\n\n"):
            if "Sentence:" in entry and "Translation:" in entry:
                machine_translation = (
                    entry.split("Sentence:")[1].split("Translation:")[0].strip()
                )
                user_lang_sentence = entry.split("Translation:")[1].strip()
                sentences.append(
                    {"sentence": user_lang_sentence, "translation": machine_translation}
                )

        # Second pass: Filter down to the best 5 sentences
        second_pass_prompt = f"""You are an expert language tutor selecting the best practice sentences for a student learning {deck.study_language}. Their native language is {deck.user_language}.
        
        Here are 10 sentences with their translations:

        {first_pass_text}

        Your task is to select the 5 best sentences from this list. Consider the following criteria:
        1. Variety of terms used
        2. Clarity and naturalness of the sentences
        3. Usefulness in everyday conversations
        4. Appropriate difficulty level for a beginner

        Present your selected sentences in the same format as they were given, with no additional commentary."""

        second_pass_message = anthropic.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1000,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": second_pass_prompt,
                        }
                    ],
                }
            ],
        )

        # Extract and process the filtered sentences
        second_pass_text = second_pass_message.content[0].text

        filtered_sentences = []
        for entry in second_pass_text.split("\n\n"):
            if "Sentence:" in entry and "Translation:" in entry:
                machine_translation = (
                    entry.split("Sentence:")[1].split("Translation:")[0].strip()
                )
                user_lang_sentence = entry.split("Translation:")[1].strip()
                filtered_sentences.append(
                    {"sentence": user_lang_sentence, "translation": machine_translation}
                )

        # Shuffle the final sentences for additional randomness
        random.shuffle(filtered_sentences)

        for sentence in filtered_sentences:
            new_sentence = GeneratedSentence(
                deck_id=deck_id,
                sentence=sentence["sentence"],
                machine_translation=sentence["translation"],
            )
            db.session.add(new_sentence)
        db.session.commit()

        return jsonify(
            {
                "deck_id": deck_id,
                "deck_name": deck.deck_name,
                "generated_sentences": filtered_sentences,
            }
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@prompts_bp.route("/sentences/<int:sentence_id>/translate", methods=["POST"])
def translate_sentence(sentence_id):
    sentence = GeneratedSentence.query.get_or_404(sentence_id)
    deck = Deck.query.get_or_404(sentence.deck_id)
    data = request.json

    if "translation" not in data:
        return jsonify({"error": "Translation is required"}), 400

    original_sentence = sentence.sentence
    machine_translation = sentence.machine_translation
    user_translation = data["translation"]

    prompt = "Your task to evaluate my performance on a translation task.\n"
    prompt += f"This is the sentence I attempted to translate from {deck.user_language} to {deck.study_language}:\n"
    prompt += original_sentence + "\n"
    prompt += "This is my translation of the sentence:\n"
    prompt += data["translation"] + "\n"
    prompt += "This was the original translation of the sentence that you generated:"
    prompt += machine_translation + "\n"
    prompt += "Please provide feedback to me based on the original machine translation, as well as your own insight.\n"
    prompt += "Note that the user's translation does not have to directly match the original machine's translation.\n"
    prompt += "If you feel the user's translation is different yet still adequate, reflect that in your rating and review.\n"
    prompt += "However, please still critique heavily on any grammatical, spelling, or logical errors.\n"
    prompt += "Please format your feedback in the following way:\n"
    prompt += "Rating: {number from 1 to 10, out of 10}\n"
    prompt += "Review: {brief and concise review of my translation and what to focus on & change.}\n"
    prompt += "ONLY PROVIDE the ratings and reviews strictly in the above format and NOTHING ELSE."

    try:
        message = anthropic.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=300,
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

        evaluation = message.content[0].text

        # Parse the evaluation
        rating_match = re.search(r"Rating: (\d+)", evaluation)
        text_match = re.search(r"Review: (.+)", evaluation, re.DOTALL)

        if rating_match and text_match:
            evaluation_rating = int(rating_match.group(1))
            evaluation_text = text_match.group(1).strip()
        else:
            raise ValueError("Failed to parse evaluation response")

        sentence.user_translation = user_translation
        sentence.evaluation_rating = evaluation_rating
        sentence.evaluation_text = evaluation_text

        db.session.commit()

        return jsonify(
            {
                "id": sentence.id,
                "sentence": sentence.sentence,
                "machine_translation": sentence.machine_translation,
                "user_translation": sentence.user_translation,
                "evaluation_rating": sentence.evaluation_rating,
                "evaluation_text": sentence.evaluation_text,
                "created_at": sentence.created_at.isoformat(),
            }
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
