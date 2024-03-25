from collections import namedtuple

from devatrans import DevaTrans

import util.gpt.word_operations as gpt
from util.translation import translate_text
from util.transliteration.el import get_greek_transliteration
from util.transliteration.hi import get_indic_transliteration
from util.transliteration.ja import get_japanese_transliteration
from util.transliteration.zh import get_chinese_transliteration
from util.vocab_db import VocabDB
from util.word_splitter import WordSplitter


class Term:
    def __init__(self,
                 text,
                 position=-1,
                 translation=None,
                 transliteration=None,
                 ):
        self.text = text
        self.position = position
        self.translation = translation
        self.transliteration = transliteration


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


def transliterate_term(term: Term, from_lang: str):
    if from_lang == "hi":
        term.transliteration = get_indic_transliteration(term.text)
    if from_lang == "ja":
        term.transliteration = get_japanese_transliteration(term.text)
    if from_lang == "zh":
        term.transliteration = get_chinese_transliteration(term.text)
    if from_lang == "el":
        term.transliteration = get_greek_transliteration(term.text)


def transliterate_terms(terms: list[Term], from_lang: str):
    for term in terms:
        transliterate_term(term, from_lang)


def translate_term(term: Term, from_lang: str, to_lang: str):
    vdb = VocabDB(from_lang)
    if vdb.has(term.text):
        term.translation = vdb.get_translation(term.text, to_lang)
    if not term.translation:
        term.translation = translate_text(term.text, from_lang, to_lang)
        vdb.write_translation(term.text,
                              to_lang,
                              term.translation)


def translate_terms(terms: list[Term], from_lang: str, to_lang: str):
    for term in terms:
        translate_term(term, from_lang, to_lang)


def translate_sentences(terms: list[Term], from_lang: str, to_lang: str):
    for term in terms:
        term.translation = translate_text(term.text, from_lang, to_lang)


def get_translation_json(text, from_lang) -> dict:
    sentences: list[Term] = get_sentences(text)
    word_group_strs: list[str] = []
    for sentence in sentences:
        print(f"Getting word splits for sentence {sentences.index(sentence)+1}/{len(sentences)}")
        word_group_strs += get_and_update_word_splits(sentence.text, from_lang)
    word_groups: list[Term] = _term_str_to_terms(text, word_group_strs)

    translate_terms(word_groups, from_lang, "en")
    translate_sentences(sentences, from_lang, "en")

    transliterate_terms(word_groups, from_lang)
    transliterate_terms(sentences, from_lang)

    return {
        "terms": [w.__dict__ for w in word_groups],
        "sentences": [s.__dict__ for s in sentences],
    }
