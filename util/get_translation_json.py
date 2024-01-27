from collections import namedtuple

from devatrans import DevaTrans

import util.gpt as gpt
from util.translation import translate_text
from util.vocab_db import VocabDB
from util.word_splitter import WordSplitter


class Term:
    def __init__(self,
                 text,
                 position=-1,
                 translation=None,
                 transliteration=None,
                 infinitive=None,
                 infinitive_translation=None,
                 infinitive_transliteration=None,
                 ):
        self.text = text
        self.position = position
        self.translation = translation
        self.transliteration = transliteration
        self.infinitive = infinitive
        self.infinitive_translation = infinitive_translation
        self.infinitive_transliteration = infinitive_transliteration


def get_and_update_word_splits(text, from_lang):
    w = WordSplitter(from_lang)
    vdb = VocabDB(from_lang)
    word_groups = w.split_text_into_word_groups(text)
    vdb.write_words(word_groups)
    return word_groups


def get_word_groups(text, from_lang) -> list[Term]:
    word_groups: list[str] = get_and_update_word_splits(text, from_lang)
    return _term_str_to_terms(text, word_groups)


def _term_str_to_terms(text: str, term_strs: list[str]) -> list[Term]:
    text_copy = text
    terms: list[Term] = []
    for term_str in term_strs:
        position = text_copy.find(term_str)
        length = len(term_str)
        text_copy = text_copy.replace(term_str, "."*length, 1)
        terms.append(Term(text=term_str, position=position))
    return terms


def get_sentences(text):
    sentence_strs = text.split("\n")
    sentence_strs = [s.strip() for s in sentence_strs]
    sentences: list(Term) = [Term(text=s, position=sentence_strs.index(
        s)) for s in sentence_strs if len(s) > 0]
    return sentences


def split_syllables_transliterated(word):
    vowels = {'a', 'e', 'i', 'o', 'u', "ā", "ū", "ī", "़"} # Add nukta (़), because DevaTrans messes it up
    syllables = []
    current_syllable = ''
    for i, char in enumerate(word):
        has_any_vowel = any([vowel in current_syllable for vowel in vowels])
        if char not in vowels and \
                current_syllable != '' and \
                has_any_vowel:
            syllables.append(current_syllable)
            current_syllable = ''
        current_syllable += char
    if current_syllable != '':
        syllables.append(current_syllable)
    return syllables


def ends_with_matra(word):
    matra_start = 0x093E
    matra_end = 0x094C
    last_char = word[-1]
    return matra_start <= ord(last_char) <= matra_end



def apply_a_dropping_rules(word, transliteration):
    # Remove 'a' from the end of the word
    removed_unnecessary_a_at_end_of_words = transliteration[:-
                                                            1] if transliteration.endswith("a") else transliteration
    syllables = split_syllables_transliterated(
        removed_unnecessary_a_at_end_of_words)
    # Remove 'a' from the second letter in a 3-letter-word that ends in a Matra
    if ends_with_matra(word) and len(syllables) == 3 and syllables[1][-1] == 'a':
        syllables[1] = syllables[1][:-1]
    # Remove 'a' from the second letter in a 4-letter-word that does NOT end in a Matra
    if (not ends_with_matra(word)) and len(syllables) == 4 and syllables[1][-1] == 'a':
        syllables[1] = syllables[1][:-1]
    # Remove 'a' from the third letter in a 4-letter-word that ends in a Matra
    if ends_with_matra(word) and len(syllables) == 4 and syllables[2][-1] == 'a':
        syllables[2] = syllables[2][:-1]
    return "".join(syllables)


def fix_nukta(transliteration):
    nukta = "़"
    syllables = split_syllables_transliterated(transliteration)
    for i, syllable in enumerate(syllables):
        if nukta in syllable:
            if syllable[0] == "ḍ":
                syllables[i] = syllables[i].replace(nukta,"").replace("ḍ","ṛ")
            else:
                syllables[i] = syllables[i].replace(nukta,"")
    return "".join(syllables)


def replace_wrong_latin_letters(transliteration):
    return transliteration\
        .replace("ch", "------")\
        .replace("c", "ch")\
        .replace("------", "chh")


# test cases
# छिड़कते = chhiṛakte
# लड़का = laṛkā

def get_indic_transliteration_for_word(word):
    dt = DevaTrans()
    deva_transliteration = dt.transliterate(
        input_type="sen", to_convention="iast", sentence=word)
    without_wrong_nukta = fix_nukta(deva_transliteration)
    with_dropped_as = apply_a_dropping_rules(word, without_wrong_nukta)
    with_replaced_letters = replace_wrong_latin_letters(with_dropped_as)
    return with_replaced_letters


def get_indic_transliteration(text):
    return " ".join([get_indic_transliteration_for_word(word) for word in text.split(" ")])


def transliterate_term(term: Term, from_lang: str):
    if from_lang == "hi":
        term.transliteration = get_indic_transliteration(term.text)
        if term.infinitive:
            term.infinitive_transliteration = get_indic_transliteration(
                term.infinitive)


def transliterate_terms(terms: list[Term], from_lang: str):
    for term in terms:
        transliterate_term(term, from_lang)


def translate_term(term: Term, from_lang: str, to_lang: str, is_infinitive=False):
    vdb = VocabDB(from_lang)
    if vdb.has(term.text):
        term.translation = vdb.get_translation(term.text, to_lang)
        term.infinitive = vdb.get_infinitive(term.text)
    if not term.translation or not term.infinitive:
        if not term.translation:
            term.translation = translate_text(term.text, from_lang, to_lang)
        if not term.infinitive:
            term.infinitive = gpt.get_infinitive(
                term.text) if not is_infinitive else term.text
        vdb.write_translation(term.text,
                              to_lang,
                              term.translation,
                              term.infinitive)
    if term.infinitive != term.text and not is_infinitive:
        translate_term(Term(text=term.infinitive), from_lang,
                       to_lang, is_infinitive=True)
    term.infinitive_translation = vdb.get_translation(term.infinitive, to_lang)


def translate_terms(terms: list[Term], from_lang: str, to_lang: str):
    for term in terms:
        translate_term(term, from_lang, to_lang)


def translate_sentences(terms: list[Term], from_lang: str, to_lang: str):
    for term in terms:
        term.translation = translate_text(term.text, from_lang, to_lang)


def get_translation_json(text, from_lang, to_lang) -> dict:
    sentences: list[Term] = get_sentences(text)
    word_group_strs: list[str] = []
    for sentence in sentences:
        word_group_strs += get_and_update_word_splits(sentence.text, from_lang)
    word_groups: list[Term] = _term_str_to_terms(text, word_group_strs)

    translate_terms(word_groups, from_lang, to_lang)
    translate_sentences(sentences, from_lang, to_lang)

    transliterate_terms(word_groups, from_lang)
    transliterate_terms(sentences, from_lang)

    return {
        "terms": [w.__dict__ for w in word_groups],
        "sentences": [s.__dict__ for s in sentences],
    }


if __name__ == "__main__":
    split_syllables_transliterated("kakalu")
