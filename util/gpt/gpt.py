import json
import random
from openai import OpenAI

from util.db import get_texts_stories_in_collection

client = OpenAI()


def get_next_message(messages, system_prompt):
    chat_completion = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "system", "content": system_prompt}] + messages,
    )
    return {key: chat_completion.choices[0].message.__dict__[key] for key in ["content", "role"]}


def single_chat_completion(prompt, temperature=1, model="gpt-4-1106-preview"):
    chat_completion = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[{"role": "user", "content": prompt}],
    )
    return chat_completion.choices[0].message.content


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