from openai import OpenAI

client = OpenAI()


def get_next_message(messages, system_prompt):
    chat_completion = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "system", "content": system_prompt}] + messages,
    )
    return {key: chat_completion.choices[0].message.__dict__[key] for key in ["content", "role"]}


def text_to_word_groups(sentence) -> list[str]:
    split_prompt = "Please mark the word boundaries in the following with a \"|\". Dont split word groups. Remove all punctuation, new lines and quotation. Remove all characters that are not letters: "
    chat_completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        temperature=0,
        messages=[{"role": "user", "content": split_prompt + sentence}],
    )
    word_groups = chat_completion.choices[0].message.content.split("|")
    return [word_group.strip() for word_group in word_groups if len(word_group) > 0]


def get_infinitive(word) -> str:
    prompt = f"If this word is a verb, give me the infinitive. If it is not an adjective or adverb, give me the neutral version, that would be found in a dictionary. If it is another type of word, just give me back the word. Do not give any commentrary. Here is the word: {word}"
    chat_completion = client.chat.completions.create(
        model="gpt-4-1106-preview",
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
    )
    return chat_completion.choices[0].message.content
