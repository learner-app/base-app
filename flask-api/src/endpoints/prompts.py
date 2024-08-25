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

    user_lang_given = request.args.get("user_lang_given", "false").lower() == "true"
    sentence_count = int(request.args.get("count"))
    print("Sentence Count", sentence_count)

    if not all_terms:
        return jsonify({"error": "No terms found in this deck"}), 400

    num_terms_to_emphasize = min(len(all_terms), sentence_count)
    random.shuffle(all_terms)
    emphasized_terms = all_terms[:num_terms_to_emphasize]
    contextual_terms = all_terms[num_terms_to_emphasize:]

    # Create the terms list, with contextual terms first and emphasized terms last
    terms_list = "Contextual Terms:\n"
    terms_list += "\n".join(
        f"Term: {term.term} : {term.definition}" for term in contextual_terms
    )

    emphasized_terms_list = "\nKey Terms to Emphasize:\n"
    emphasized_terms_list += "\n".join(
        f"Term: {term.term} : {term.definition}" for term in emphasized_terms
    )

    print(emphasized_terms_list)

    # TODO: Remove the line about complicated sentence structures depending on beginner, advanced, intermediate, etc. on rule 3.

    first_prompt = f"""You are an expert language tutor creating practice sentences for a student learning {deck.deck_language}. Their native language is {deck.user_language}.
    Here is a list of terms and their definitions that the student is learning:

    {terms_list}
    {emphasized_terms_list}

    Your task is to create {sentence_count} example {deck.deck_language} sentences and their {deck.user_language} translations, each focusing on one of the Key Terms. Follow these guidelines:

    1. Create one sentence for each of the Key Terms listed at the end. Each sentence should primarily demonstrate the usage of its assigned Key Term.
    2. You can and are encouraged to use the Contextual Terms and other Key Terms to create more natural sentences and provide context, but the main focus should be on the assigned Key Term for each sentence.
    3. IMPORTANT: Use the exact terms and definitions provided in the term list. Do not use synonyms or alternative phrasings for these terms.
    4. Refrain from using complex vocabulary or grammar that is not in the term list. However, you may use common words known to beginners. You may also occasionally use more complicated sentence structures.
    5. Ensure both the {deck.deck_language} sentences and their {deck.user_language} translations are grammatically correct.
    6. Create sentences that are natural and suitable for everyday conversations and practical scenarios.
    7. Only use more than one sentence for your example when absolutely necessary.
    8. After each sentence, list only the Contextual and Key Terms used in that sentence, with the Key Term listed first. Ensure that the terms you include are actually in the list of terms above and are used in their exact form.
    9. Most importantly, ensure that the sentence generated makes complete logical sense.

    Present your examples in this format:
    Sentence: {{example sentence in {deck.deck_language}}}
    Translation: {{corresponding translation in {deck.user_language}}}
    Terms used: {{semicolon-separated list of terms used in this sentence, starting with the Key Term, using the exact form provided in the term list, including both {deck.deck_language} and {deck.user_language} versions}}
    New terms: {{semicolon-separated list of new vocabulary terms in the same format term : def used in this sentence that are not in the lists above.}}

    If there are no new terms, keep "New terms:" and nothing afterwards.

    Remember:
    1. Always use the exact terms from the provided list. Do not substitute them with synonyms or rephrase them.
    2. Ensure the sentences are logical and sensical.
    3. Provide ONLY the examples in the specified format, with no additional commentary."""

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
                if user_lang_given:
                    translation = sentence_parts[0].split("Sentence:")[1].strip()
                    sentence = sentence_parts[1].split("Translation:")[1].strip()
                else:
                    sentence = sentence_parts[0].split("Sentence:")[1].strip()
                    translation = sentence_parts[1].split("Translation:")[1].strip()
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
                user_lang_given=user_lang_given,
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
                "user_lang_given": user_lang_given,
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
    terms_used = sentence.terms_used

    if sentence.user_lang_given:
        original_lang = deck.user_language
        translated_lang = deck.deck_language
    else:
        original_lang = deck.deck_language
        translated_lang = deck.user_language

    prompt = f"""
        Your task is to evaluate my performance on a translation task.

        Original sentence (in {original_lang}):
        {original_sentence}

        My translation (in {translated_lang}):
        {user_translation}

        Machine translation (for reference):
        {machine_translation}

        Terms used in this exercise:
        {terms_used}

        Please provide feedback based on the information provided above. Your feedback should consist of a rating and a review.

        Rating criteria:
        - Mainly based on accuracy of vocabulary and grammar
        - Scale: 1 to 10, where:
        1: Very Poor (no attempt given)
        2-3: Poor (major errors in vocabulary and grammar)
        4-5: Fair (some significant errors, but a good attempt and partially correct)
        6-8: Good (minor errors, mostly accurate)
        9: Excellent (very negligible errors)
        10: Perfect (fully accurate in meaning and grammar)

        Review guidelines:
        - Evaluate my translation primarily based on how well it conveys the meaning of the original sentence
        - My translation can use different words or grammatical structures as long as the meaning is preserved
        - When referencing the machine translation, only mention specific words or phrases that are actually present in it
        - Do not claim that the machine translation used certain words or structures unless you can directly quote them
        - Highlight both strengths and areas for improvement in my translation
        - Provide specific feedback on any grammatical, spelling, or logical errors you can identify
        - If my translation is different from the machine translation but still accurate and appropriate, reflect this positively
        - IMPORTANT: Use the exact terms provided in the "Terms used" section. Do not suggest alternative translations for these terms.

        Please format your feedback exactly as follows:

        Rating: {{number from 1 to 10}}
        Review: {{brief and concise review of the translation, focusing on accuracy, grammar, and any necessary improvements}}

        Note: If my translation is perfectly accurate and grammatically correct, don't hesitate to give a 10!

        IMPORTANT:
        1. When discussing the machine translation, only reference words or phrases that are explicitly present in it.
        2. Focus on evaluating my translation's accuracy in conveying the original meaning, not on matching the machine translation exactly.
        3. Keep the reviews short and concise, ensuring that there are no unnecessary details or elaborations.
        4. Provide ONLY the Rating and Review in the specified format. Do not include any other text or explanations.
        """
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
