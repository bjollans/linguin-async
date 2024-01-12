import json
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


def get_questions_for_story(story) -> list[dict]:
    prompt = '''Give me 10 multiple choice questions to this text. The questions should have 4 possible answers, 1 should be the correct one (mark this one with a *), 3 should be incorrect. The questions are intended to test the reading comprehension of an English language learner, so the answers should not be obvious. Return the questions in the following json format:
```
{"question":"...", "correctAnswer":"...", "otherOptions":["...", "...", "..."]}
```
Just return the plain JSON without formatting or backticks.
Here is the text:
"""
''' + story + '\n"""'
    return chat_completion([{"role": "user", "content": prompt}])


def chat_completion(chat_json, temperature=1, model="gpt-4-1106-preview"):
    chat_completion = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=chat_json,
    )
    return chat_completion.choices[0].message.content


def chain_of_thought(prompts: list[str]) -> str:
    answers = []
    for i, _ in enumerate(prompts):
        prompts_to_use = [{"role": "user", "content": prompt}
                          for prompt in prompts[:i+1]]
        answers_to_use = [{"role": "assistant", "content": answer}
                          for answer in answers[:i]]

        chat_history = [val for pair in zip(
            prompts_to_use, answers_to_use) for val in pair] + [prompts_to_use[-1]]
        answers.append(chat_completion(chat_history, model='gpt-3.5-turbo'))
    return answers[-1]


def generate_non_fiction_story(topic, paragraph_count=3):
    return chain_of_thought([
        f"What do you know about {topic}. Give me {paragraph_count} paragraphs:",
        "Simplify the language and use more common words.",
        "Put every sentence in a new line.",
    ])


def generate_known_fiction_story(title, paragraph_count=3):
    return chain_of_thought([
        f'Tell me the story "{title}" in {paragraph_count} paragraphs:',
        "Simplify the language and use more common words.",
        "Put every sentence in a new line.",
    ])
