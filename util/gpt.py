from openai import OpenAI

client = OpenAI()


def get_next_message(messages, system_prompt):
    chat_completion = client.chat.completions.create( \
        model="gpt-4-1106-preview", \
        messages=[{"role": "system", "content": system_prompt}] + messages, \
    )
    return {key: chat_completion.choices[0].message.__dict__[key] for key in ["content", "role"]}