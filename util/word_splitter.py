import unicodedata
from util import gpt
from util.vocab_db import VocabDB


class WordSplitter:
    def __init__(self, from_lang) -> None:
        self.from_lang = from_lang
        self.vocab_db = VocabDB(from_lang)

    @staticmethod
    def _remove_non_letters(input_string):
        result = ''.join(char for char in input_string if unicodedata.category(char).startswith(('L', 'Mn', 'Mc')))
        return result
    
    def split_text_into_words(self, text) -> list[str]:
        if self.from_lang == "ja" or self.from_lang == "zh":
            words: list[str] = gpt.text_to_word_groups(text)
        else:
            words: list[str] = text.split(" ")
        return [WordSplitter._remove_non_letters(word) for word in words]

    def concatenate_words(self, words: list[str]):
        separator = " "
        if self.from_lang == "ja" or self.from_lang == "zh":
            separator = ""
        return separator.join(words)


    def split_text_into_word_groups(self, text):
        words: list[str] = self.split_text_into_words(text)
        word_groups: list[str] = []
        max_word_group_len = 5
        i=0
        while i < len(words):
            for j in range(max_word_group_len, 0, -1):
                word_group = self.concatenate_words(words[i:i+j])
                if j==1 or self.vocab_db.has(word_group):
                    word_groups.append(word_group)
                    i+=j-1
                    break
            i+=1
        return [w for w in word_groups if w != ""]