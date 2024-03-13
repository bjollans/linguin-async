from util.gpt.gpt import single_chat_completion


def text_to_word_groups(sentence) -> list[str]:
    prompt = "Please mark the word boundaries in the following with a \"|\". Dont split word groups. Remove all punctuation, new lines and quotation. Remove all characters that are not letters: "
    word_groups = single_chat_completion(prompt).split("|")
    return [word_group.strip() for word_group in word_groups if len(word_group) > 0]


def get_infinitive(word) -> str:
    prompt = f"If this word is a verb, give me the infinitive. If it is not an adjective or adverb, give me the neutral version, that would be found in a dictionary. If it is another type of word, just give me back the word. Do not give any commentrary. Here is the word: {word}"
    return single_chat_completion(prompt)