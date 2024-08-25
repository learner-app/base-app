# base-app
To setup local DB, go to the flask-api directory and run ./setup/setupdb.sh

To set up local servers, run `flask run (--debug)` in flask-api directory.
Then run `npm start` in react-app directory.

Then everything should should run at localhost:3000.


# filtering prompt not currently used

Second message: Select the best sentences
second_prompt = f"""Now, review the sentences you just generated. Select the sentences that meet the following criteria:
1. The sentence clearly demonstrates the usage of its assigned Key Term.
2. The sentence avoids excessive use of difficult vocabulary that is not in the list of terms.
3. The sentence has absolutely correct grammar usage.
4. Most importantly, ensure that the sentence makes logical sense.
5. Lastly, the "Terms Used" must only contains terms from the provided list of terms. If the sentence follows all of the above rules but only fails this one, you may choose to remove the term from the "Terms Used" list and include the sentence in the final list.

You must choose at least 5 sentences to keep, but can choose to keep all of them if they all properly follow the criteria above.
Don't be scared to keep all 10 if they are all appropriate!

Present your selected sentences in the same format as before, with no additional commentary."""

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

generated_text = second_response.content[0].text
print("second generation")
print(generated_text)