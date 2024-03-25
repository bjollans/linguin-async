from util.gpt.gpt import single_chat_completion


def text_to_word_groups(sentence) -> list[str]:
    prompt = f"Please mark the word boundaries in the following with a \"|\". Dont split word groups. Remove all punctuation, new lines and quotation. Remove all characters that are not letters: {sentence}"
    word_groups = single_chat_completion(prompt).split("|")
    return [word_group.strip() for word_group in word_groups if len(word_group) > 0]