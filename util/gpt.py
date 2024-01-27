import json
import random
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
    return json.loads(chat_completion([{"role": "user", "content": prompt}]))


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
        print(f"Chain of thought: {i+1}/{len(prompts)}")
        prompts_to_use = [{"role": "user", "content": prompt}
                          for prompt in prompts[:i+1]]
        answers_to_use = [{"role": "assistant", "content": answer}
                          for answer in answers[:i]]

        chat_history = [val for pair in zip(
            prompts_to_use, answers_to_use) for val in pair] + [prompts_to_use[-1]]
        answers.append(chat_completion(
            chat_history, model='gpt-4-1106-preview'))
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

def chain_of_thought_with_image(prompts: list[str], image_url) -> str:
    answers = [react_to_image(prompts[0], image_url)]
    for i, _ in enumerate(prompts):
        if i==0: continue
        print(f"Chain of thought: {i+1}/{len(prompts)}")
        prompts_to_use = [{"role": "user", "content": prompt}
                          for prompt in prompts[:i+1]]
        answers_to_use = [{"role": "assistant", "content": answer}
                          for answer in answers[:i]]

        chat_history = [val for pair in zip(
            prompts_to_use, answers_to_use) for val in pair] + [prompts_to_use[-1]]
        answers.append(chat_completion(
            chat_history, model='gpt-4-1106-preview'))
    return answers[-1]


def react_to_image(text, image_url):
    chat_completion = client.chat.completions.create(
        model="gpt-4-vision-preview",
        temperature=1,
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": text},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url,
                        },
                    },
                ],
            }
        ],
    )
    return chat_completion.choices[0].message.content

def generate_mini_story():
    img_url = f'https://mini-story-images.s3.eu-west-1.amazonaws.com/{random.randint(0,80)}.jpeg'
    prompt = 'Write me a short story (and title) based on this picture in json format as `{"title":"...","story":"..."}`. Just return the plain JSON without formatting or backticks. The story should be for an A1 English learner. It should be around 2 paragraphs long. It should be set in India, but do not mention "India" or elude to it in the story. Write the story using the Heros Journey structure. Start with the hero in a normal setting, introduce a challenge that leads them on an adventure. Have them face obstacles, receive help from a mentor, and overcome a major crisis. Conclude with the hero returning transformed, bringing back something valuable to their original home. Do not use words like "Hero" or "Quest". The setting should be general day to day and not epic.'
    # chain_of_thought_with_image...
    # chain_of_thought_with_image...
    # chain_of_thought_with_image...
    # chain_of_thought_with_image...
    # chain_of_thought_with_image...
    # chain_of_thought_with_image...
    # chain_of_thought_with_image...
    # chain_of_thought_with_image...
    # chain_of_thought_with_image...
    # chain_of_thought_with_image...
    # chain_of_thought_with_image...
    return react_to_image(prompt, img_url)