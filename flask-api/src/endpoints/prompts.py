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

    num_terms_to_emphasize = min(len(all_terms), 8)
    random.shuffle(all_terms)
    emphasized_terms = all_terms[:num_terms_to_emphasize]
    contextual_terms = all_terms[num_terms_to_emphasize:]

    # Create the terms list, with contextual terms first and emphasized terms last
    terms_list = "Contextual Terms:\n"
    terms_list += "\n".join(
        f"Term: {term.term}\nDefinition: {term.definition}" for term in contextual_terms
    )

    emphasized_terms_list = "\nKey Terms to Emphasize:\n"
    emphasized_terms_list += "\n".join(
        f"Term: {term.term}\nDefinition: {term.definition}" for term in emphasized_terms
    )

    print(emphasized_terms_list)

    # TODO: Remove the line about complicated sentence structures depending on beginner, advanced, intermediate, etc. on rule 3.

    first_prompt = f"""You are an expert language tutor creating practice sentences for a student learning {deck.study_language}. Their native language is {deck.user_language}.
    Here is a list of terms and their definitions that the student is learning:

    {terms_list}
    {emphasized_terms_list}

    Your task is to create {num_terms_to_emphasize} example {deck.study_language} sentences and their {deck.user_language} translations, each focusing on one of the Key Terms. Follow these guidelines:

    1. Create one sentence for each of the Key Terms listed at the end. Each sentence should primarily demonstrate the usage of its assigned Key Term.
    2. You can and are encouraged to use the Contextual Terms and other Key Terms to create more natural sentences and provide context, but the main focus should be on the assigned Key Term for each sentence.
    3. Refrain from using complex vocabulary or grammar that is not in the term list. However, you may use common adjacent words known to beginners. You may also occasionally use more complicated sentence structures.
    4. Ensure both the {deck.study_language} sentences and their {deck.user_language} translations are grammatically correct.
    5. Create sentences that are natural and suitable for everyday conversations and practical scenarios.
    6. After each sentence, list only the Contextual and Key Terms used in that sentence, with the Key Term listed first. Ensure that the terms you include are actually in the list of terms above.
    7. Most importantly, ensure that the sentence generated makes complete logical sense.
   
    Present your examples in this format:
    Sentence: {{example sentence in {deck.study_language}}}
    Translation: {{corresponding translation in {deck.user_language}}}
    Terms used: {{comma-separated list of terms used in this sentence, starting with the Key Term}}

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

        print("first generation")
        print(generated_text)

        # # Second message: Select the best sentences
        # second_prompt = f"""Now, review the sentences you just generated. Select the sentences that meet the following criteria:
        # 1. The sentence clearly demonstrates the usage of its assigned Key Term.
        # 2. The sentence avoids excessive use of difficult vocabulary that is not in the list of terms.
        # 3. The sentence has absolutely correct grammar usage.
        # 4. Most importantly, ensure that the sentence makes logical sense.
        # 5. Lastly, the "Terms Used" must only contains terms from the provided list of terms. If the sentence follows all of the above rules but only fails this one, you may choose to remove the term from the "Terms Used" list and include the sentence in the final list.

        # You must choose at least 5 sentences to keep, but can choose to keep all of them if they all properly follow the criteria above.
        # Don't be scared to keep all 10 if they are all appropriate!

        # Present your selected sentences in the same format as before, with no additional commentary."""

        # # Second API call to select the best sentences
        # second_response = anthropic.messages.create(
        #     model="claude-3-5-sonnet-20240620",
        #     max_tokens=500,
        #     messages=[
        #         {
        #             "role": "user",
        #             "content": first_prompt,
        #         },
        #         {
        #             "role": "assistant",
        #             "content": generated_text,
        #         },
        #         {
        #             "role": "user",
        #             "content": second_prompt,
        #         },
        #     ],
        # )

        # # Process the selected sentences
        # generated_text = second_response.content[0].text
        # print("second generation")
        # print(generated_text)

        # TODO: may have to do a manual check of terms used here.
        selected_sentences = []
        for entry in generated_text.strip().split("\n\n"):
            if (
                "Sentence:" in entry
                and "Translation:" in entry
                and "Terms used:" in entry
            ):
                sentence_parts = entry.split("\n")
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
    prompt += (
        "However, please still critique any grammatical, spelling, or logical errors.\n"
    )
    prompt += "Please format your feedback in the following way:\n"
    prompt += "Rating: {number from 1 to 10, out of 10}\n"
    prompt += "Review: {brief and concise review of my translation and what to focus on & change.}\n"
    prompt += "If my translation means the same thing as the original sentence and is grammatically correct, don't be afraid to a give perfect 10!"
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
