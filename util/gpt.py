from openai import OpenAI

client = OpenAI()


def get_next_message(messages, system_prompt):
    chat_completion = client.chat.completions.create( \
        model="gpt-4-1106-preview", \
        messages=[{"role": "system", "content": system_prompt}] + messages, \
    )
    return {key: chat_completion.choices[0].message.__dict__[key] for key in ["content", "role"]}

def text_to_word_groups(sentence) -> list[str]:
    split_prompt = "Please mark the word boundaries in the following with a \"|\". Dont split word groups. Remove all punctuation: "
    chat_completion = client.chat.completions.create( \
        model="gpt-4-1106-preview", \
        messages=[{"role": "user", "content": split_prompt + sentence}], \
    )
    word_groups = chat_completion.choices[0].message.content.split("|")
    return [word_group.strip() for word_group in word_groups if len(word_group) > 0]