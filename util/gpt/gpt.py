import json
import random
from openai import OpenAI

from util.db import get_texts_stories_in_collection

client = OpenAI()


def get_next_message(messages, system_prompt):
    chat_completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": system_prompt}] + messages,
    )
    return {key: chat_completion.choices[0].message.__dict__[key] for key in ["content", "role"]}


def single_chat_completion(prompt, temperature=1, model="gpt-4o", type="text", max_tokens=1024, top_p=1, system_prompt=None):
    messages = []
    if system_prompt:
        messages.append({"role": "system","content":system_prompt})
    messages.append({"role": "user", "content": prompt})
    chat_completion = client.chat.completions.create(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        messages=messages,
        response_format={ "type": type },
    )
    return chat_completion.choices[0].message.content


def chat_completion(chat_json, temperature=1, model="gpt-4o", type="text", max_tokens=None):
    chat_completion = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=chat_json,
        max_tokens=max_tokens,
        response_format={ "type": type },
    )
    return chat_completion.choices[0].message.content


def chain_of_thought(prompts: list[str], type="text") -> str:
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
            chat_history, model='gpt-4o', type=type))
    return answers[-1]

def chain_of_thought_with_image(prompts: list[str], image_url, model='gpt-4o') -> str:
    print(f"Chain of thought: {1}/{len(prompts)}")
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
            chat_history, model=model, max_tokens=2048))
    return answers[-1]

def chain_of_thought_with_image_final_result_json(prompts: list[str], image_url, model='gpt-4o', system_prompt: str = None) -> str:
    print(f"Chain of thought: {1}/{len(prompts)}")
    answers = [react_to_image(prompts[0], image_url, system_prompt=system_prompt)]
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
            chat_history, model=model, max_tokens=2048, 
            type="json_object" if i == len(prompts) -1 else "text"))
    return answers[-1]

def react_to_image(text, image_url, system_prompt=None):
    messages = []
    if system_prompt:
        messages.append({"role": "system","content":system_prompt})
    messages.append({
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
            })
    chat_completion = client.chat.completions.create(
        model="gpt-4o",
        temperature=1,
        max_tokens=2048,
        messages=messages,
    )
    return chat_completion.choices[0].message.content
