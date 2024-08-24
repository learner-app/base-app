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
    all_terms = Term.query.filter_by(deck_id=deck_id).all()

    if not all_terms:
        return jsonify({"error": "No terms found in this deck"}), 400

    num_terms_to_emphasize = max(len(all_terms) // 5, min(5, len(all_terms)))
    emphasized_terms = random.sample(all_terms, num_terms_to_emphasize)
    contextual_terms = [term for term in all_terms if term not in emphasized_terms]

    # Create the terms list, with contextual terms first and emphasized terms last
    terms_list = "Contextual Terms:\n"
    terms_list += "\n".join(
        f"Term: {term.term}\nDefinition: {term.definition}" for term in contextual_terms
    )
    terms_list += "\n\nKey Terms to Emphasize:\n"
    terms_list += "\n".join(
        f"Term: {term.term}\nDefinition: {term.definition}" for term in emphasized_terms
    )

    first_prompt = f"""You are an expert language tutor creating practice sentences for a student learning {deck.study_language}. Their native language is {deck.user_language}.
    Here is a list of terms and their definitions that the student is learning:

    {terms_list}

    Your task is to create 10 example {deck.study_language} sentences and their {deck.user_language} translations that demonstrate the usage of these terms. Follow these guidelines:

    1. Create coherent, meaningful sentences that accurately use the terms according to their definitions.
    2. Emphasize the usage of the Key Terms listed at the end. You should try to use each of these terms at least once.
    3. You can use the Contextual Terms to create more natural sentences and provide context, but prioritize the Key Terms.
    4. Use simple language and refrain from using complex vocabulary or grammar that is not in the term list. However, you may use common words known to beginners.
    5. Ensure both the {deck.study_language} sentences and their {deck.user_language} translations are grammatically correct.
    6. Create sentences that are natural and suitable for everyday conversations and practical scenarios.
    7. After each sentence, list the terms used in that sentence.
   
    Present your examples in this format:
    Sentence: {{example sentence in {deck.study_language}}}
    Translation: {{corresponding translation in {deck.user_language}}}
    Terms used: {{comma-separated list of terms used in this sentence}}

    Provide ONLY the examples in the specified format, with no additional commentary."""

    try:
        first_response = anthropic.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1000,
            messages=[
                {
                    "role": "user",
                    "content": first_prompt,
                }
            ],
        )

        generated_text = first_response.content[0].text

        # Second message: Select the best 5 sentences
        second_prompt = f"""Now, from the 10 sentences you just generated, select the 5 best sentences. Consider the following criteria:
        1. Variety of terms used
        2. Clarity and naturalness of the sentences in both ${deck.user_language} and ${deck.study_language}
        3. Applicability of the sentence to common everyday usage
        4. Absolutely correct grammar use
        5. Avoid excessive use of vocabulary that is not in the list of terms
        6. Appropriate difficulty level, judged based on the list of terms

        Present your selected sentences in the same format as before, with no additional commentary."""

        # Second API call to select the best 5 sentences
        second_response = anthropic.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=500,
            messages=[
                {
                    "role": "user",
                    "content": first_prompt,
                },
                {
                    "role": "assistant",
                    "content": generated_text,
                },
                {
                    "role": "user",
                    "content": second_prompt,
                },
            ],
        )

        # Process the selected sentences
        generated_text = second_response.content[0].text

        selected_sentences = []
        for entry in generated_text.strip().split("\n\n"):
            if (
                "Sentence:" in entry
                and "Translation:" in entry
                and "Terms used:" in entry
            ):
                sentence_parts = entry.split("\n")
                # Sentence is the machine translation, machine translation is the sentence
                translation = sentence_parts[0].split("Sentence:")[1].strip()
                sentence = sentence_parts[1].split("Translation:")[1].strip()
                terms_used = sentence_parts[2].split("Terms used:")[1].strip()
                selected_sentences.append(
                    {
                        "sentence": sentence,
                        "translation": translation,
                        "terms_used": terms_used,
                    }
                )

        for sentence in selected_sentences:
            new_sentence = GeneratedSentence(
                deck_id=deck_id,
                sentence=sentence["sentence"],
                machine_translation=sentence["translation"],
                terms_used=sentence["terms_used"],
            )
            db.session.add(new_sentence)
        db.session.commit()

        return jsonify(
            {
                "deck_id": deck_id,
                "deck_name": deck.deck_name,
                "generated_sentences": selected_sentences,
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
    prompt += f"Note that my translation does not have to directly match the original machine's translation, but still should mean the same thing when translated to ${deck.user_language}.\n"
    prompt += "If you feel my translation is different, yet still accurate and adequate, reflect that in your rating and review.\n"
    prompt += "However, please still critique heavily on any grammatical, spelling, or logical errors.\n"
    prompt += "Please format your feedback in the following way:\n"
    prompt += "Rating: {number from 1 to 10, out of 10}\n"
    prompt += "Review: {brief and concise review of my translation and what to focus on & change.}\n"
    prompt += "If my translation means the exact same thing as the original sentence and is grammatically correct, don't be afraid to a give perfect 10!"
    prompt += "Lastly, ONLY PROVIDE the ratings and reviews strictly in the above format and NOTHING ELSE."

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
