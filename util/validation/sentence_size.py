from util.word_splitter import WordSplitter


def sentences_are_too_long(translation: str, language: str) -> bool:
    word_splitter = WordSplitter(language)
    sentences = translation.split("\n")
    sentence_count = len(sentences)
    if sentence_count < 5:
        return True
    for sentence in sentences:
        words = word_splitter.split_text_into_words(sentence)
        word_count = len(words)
        if sentence_count < 8 and word_count > 25:
            return True
        if sentence_count < 10 and word_count > 35:
            return True
        if sentence_count < 15 and word_count > 45:
            return True
        if word_count > 50:
            return True
    return False