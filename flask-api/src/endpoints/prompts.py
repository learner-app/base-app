from flask import Blueprint, jsonify, request
from src import db
from src.models import Deck, GeneratedSentence, Term
from anthropic import Anthropic
import os, re, random, json

prompts_bp = Blueprint("prompts", __name__)

# Initialize Anthropic client
anthropic = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


@prompts_bp.route("/decks/<int:deck_id>/generate_sentences", methods=["POST"])
def generate_sentences(deck_id):
    deck = Deck.query.get_or_404(deck_id)
    all_terms = Term.query.filter_by(deck_id=deck_id).all()

    user_lang_given = request.args.get("user_lang_given", "false").lower() == "true"
    sentence_count = int(request.args.get("count"))

    if not all_terms:
        return jsonify({"error": "No terms found in this deck"}), 400

    num_terms_to_emphasize = min(len(all_terms), sentence_count)
    random.shuffle(all_terms)
    emphasized_terms = all_terms[:num_terms_to_emphasize]
    contextual_terms = all_terms[num_terms_to_emphasize:]

    terms_list = "Contextual Terms:\n" + "\n".join(
        f"Term: {term.term} : {term.definition}" for term in contextual_terms
    )
    emphasized_terms_list = "\nKey Terms to Emphasize:\n" + "\n".join(
        f"Term: {term.term} : {term.definition}" for term in emphasized_terms
    )
    print("\Key Terms")
    print(emphasized_terms_list)

    all_term_set = {term.term.lower() for term in all_terms}

    first_prompt = f"""You are an expert language tutor creating practice sentences for a student learning {deck.deck_language}. Their native language is {deck.user_language}.
    Here is a list of terms and their definitions that the student is learning:

    {terms_list}
    {emphasized_terms_list}

    Your task is to create {sentence_count} example {deck.deck_language} sentences and their {deck.user_language} translations, each focusing on one of the Key Terms. Follow these guidelines:

    1. Create one sentence for each of the Key Terms in order. Each sentence should primarily demonstrate the usage of its assigned Key Term.
    2. You can and are encouraged to use the Contextual Terms and other Key Terms to create more natural sentences and provide context.
    3. IMPORTANT: Use the exact terms and definitions provided in the term list. Do not use synonyms or alternative phrasings.
    4. Refrain from using complex vocabulary or grammar that is not in the term list. You may use beginner vocabulary and occasionally more complicated sentence structures.
    5. Create sentences that are fully grammatically correct, suitable for everyday conversations and practical scenarios.
    6. Only use more than one sentence for your example when absolutely necessary.
    7. Most importantly, ensure that the sentence generated makes complete logical sense.

    Present your examples in this format:
    Sentence: {{example sentence in {deck.deck_language}}}
    Translation: {{corresponding translation in {deck.user_language}}}
    Terms used: {{term1}} ::: {{definition1}} ||| {{term2}} ::: {{definition2}} ||| ...
    New terms: {{new_term1}} ::: {{new_definition1}} ||| {{new_term2}} ::: {{new_definition2}} ||| ...

    "Terms used" should only include any terms from the Key & Contextual Terms list that were used in its corresponding sentence. You must start the list of "Terms used" for each sentence with its corresponding Key Term.
    New terms should consist of any non-beginner vocabulary AND all non-beginner grammatical phrases, conjugations, or particles that are used in the example sentence, but not included within the list of provided terms.
    Always list all new terms, regardless of whether they were included in past generated sentences.
    If there are no new terms, keep "New terms:" and nothing afterwards.

    Remember:
    1. Each sentence should focus primarily on its assigned Key Term.
    2. Always use the exact terms from the provided lists of terms. Do not substitute them with synonyms or rephrase them.
    3. Ensure the sentences are logical, free of spelling mistakes, and fully GRAMATICALLY CORRECT.
    4. Provide ONLY the examples in the specified format, with no additional commentary."""

    try:
        first_response = anthropic.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1500,
            messages=[{"role": "user", "content": first_prompt}],
        )

        generated_text = first_response.content[0].text
        print("\n\nGenerated Text:")
        print(generated_text)

        selected_sentences = []
        for entry in generated_text.strip().split("\n\n"):
            if all(
                key in entry for key in ["Sentence:", "Translation:", "Terms used:"]
            ):
                sentence_parts = entry.split("\n")
                sentence = sentence_parts[0].split("Sentence:")[1].strip()
                translation = sentence_parts[1].split("Translation:")[1].strip()
                if user_lang_given:
                    sentence, translation = translation, sentence

                terms_used = {}
                new_terms = {}
                for term_pair in sentence_parts[2].split("Terms used:")[1].split("|||"):
                    if ":::" in term_pair:
                        term, definition = term_pair.split(":::")
                        term = term.strip()
                        definition = definition.strip()
                        if term.lower() in all_term_set:
                            terms_used[term] = definition
                        else:
                            new_terms[term] = definition

                if len(sentence_parts) > 3 and "New terms:" in sentence_parts[3]:
                    for term_pair in (
                        sentence_parts[3].split("New terms:")[1].split("|||")
                    ):
                        if ":::" in term_pair:
                            term, definition = term_pair.split(":::")
                            term = term.strip()
                            definition = definition.strip()
                            if term.lower() not in all_term_set:
                                new_terms[term] = definition

                selected_sentences.append(
                    {
                        "sentence": sentence,
                        "translation": translation,
                        "terms_used": terms_used,
                        "new_terms": new_terms,
                    }
                )

        for sentence in selected_sentences:
            new_sentence = GeneratedSentence(
                deck_id=deck_id,
                user_lang_given=user_lang_given,
                sentence=sentence["sentence"],
                machine_translation=sentence["translation"],
                terms_used=sentence["terms_used"],
                new_terms=sentence["new_terms"],
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

    original_lang = (
        deck.user_language if sentence.user_lang_given else deck.deck_language
    )
    translated_lang = (
        deck.deck_language if sentence.user_lang_given else deck.user_language
    )

    prompt = f"""
        Your task is to evaluate my performance on a translation task.

        Original sentence (in {original_lang}):
        {original_sentence}

        My translation (in {translated_lang}):
        {user_translation}

        Machine translation (ONLY for reference):
        {machine_translation}

        Terms used in this exercise:
        {json.dumps(terms_used, ensure_ascii=False, indent=2)}

        Please provide feedback based on the information provided above. Your feedback should consist of a rating and a review.

        Review guidelines:
        - Evaluate my translation based on how well it conveys the meaning of the original sentence and how gramatically correct it is, NOT on how well it matches the machine translation
        - Do not claim that the machine translation used certain words or structures unless you can directly quote them
        - Provide specific feedback on ANY grammatical, spelling, vocabulary, or logical errors you can identify
        - If my translation is different from the machine translation but still accurate and appropriate, reflect this positively
        - IMPORTANT: Use the exact terms and definitions provided in the "Terms used" section. Do not suggest alternative translations for these terms.

        Rating criteria:
        - Scale: integer from 1 to 10, where:
        0-1: Very Poor (no attempt given)
        2-3: Poor (major errors in both vocabulary AND grammar)
        4-5: Fair (some significant errors, but a good attempt and partially correct)
        6-7: Decent (some errors, but the meaning gets across)
        8-9: Good (few minor errors)
        10: Excellent (accurate in meaning and grammar)

        Please format your feedback exactly as follows:

        Review: {{brief and concise review of the translation, focusing on accuracy, grammar, and any necessary improvements}}
        Rating: {{number from 1 to 10, based on your review}}

        The review should be 3 sentences maximum, only going over this limit if ABSOLUTELY necessary.
        If there are minor variations in language between my translation and the machine translation, and the accuracy and grammar does not change, please give me a 10.
        However, please continue to judge any specific vocabulary, grammatical and logical errors that alter the meaning of the sentence.

        IMPORTANT:
        1. Keep the reviews short and concise.
        2. Focus on evaluating my translation's accuracy of translating the original sentence in {original_lang}, not on matching the machine translation exactly.
        3. When discussing the machine translation, PLEASE check yourself and ONLY reference words or phrases that are explicitly present in it.
        4. Provide ONLY the Rating and Review in the specified format. Do not include any other text or explanations.
        """

    try:
        message = anthropic.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=300,
            messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}],
        )

        evaluation = message.content[0].text

        rating_match = re.search(r"Rating: (\d+)", evaluation)
        text_match = re.search(r"Review: ([\s\S]+?)(?=\nRating:|\Z)", evaluation)

        if rating_match and text_match:
            evaluation_rating = int(rating_match.group(1))
            evaluation_text = text_match.group(1).strip()
        else:
            raise ValueError("Failed to parse evaluation response")

        sentence.user_translation = user_translation
        sentence.evaluation_rating = evaluation_rating
        sentence.evaluation_text = evaluation_text

        # TODO: We may choose to make the LLM evaluate its own translation here as well.

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
