from collections import defaultdict, namedtuple
from dataclasses import asdict, dataclass
from functools import partial
import itertools
import json
from typing import List
import uuid

from devatrans import DevaTrans

from util.gpt.gpt import single_chat_completion
from util.gpt.prompts.word_splitting import get_gpt_word_splits
import util.gpt.word_operations as gpt
from util.translation import translate_text
from util.transliteration.el import get_greek_transliteration
from util.transliteration.hi import get_indic_transliteration
from util.transliteration.ja import get_japanese_transliteration
from util.transliteration.zh import get_chinese_transliteration
from util.vocab_db import VocabDB
from util.word_splitter import WordSplitter
from concurrent.futures import ThreadPoolExecutor, as_completed


@dataclass
class Kanji:
    text: str
    on: str
    kun: str
    meaning: str = None


@dataclass
class Hanzi:
    text: str
    meaning: str = None


@dataclass
class Term:
    text: str
    position: int = -1
    translation: str = None
    transliteration: str = None
    case: str = None
    word_type: str = None
    gender: str = None
    compound_id: str = None
    idiom_id: str = None
    kanjis: list[Kanji] = None
    hanzis: list[Hanzi] = None
    note: str = None

    def to_dict(self):
        return asdict(self, dict_factory=lambda x: {k: v for (k, v) in x if v != None})


@dataclass
class Compound:
    id: str
    text: str
    translation: str = None



def get_and_update_word_splits(text, from_lang):
    w = WordSplitter(from_lang)
    word_groups = w.split_text_into_word_groups(text)
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


def _add_position_to_terms(text: str, terms: list[Term]) -> list[Term]:
    text_copy = text
    for term in terms:
        position = text_copy.find(term.text)
        length = len(term.text)
        text_copy = text_copy.replace(term.text, "."*length, 1)
        term.position = position
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


def _get_word_splits_and_translation_from_gpt(sentence, from_lang):
    response_json = get_gpt_word_splits(sentence.text, from_lang)
    return _process_word_splits_and_translation_from_gpt(response_json)


def _process_word_splits_and_translation_from_gpt(response_json):
    sentence_terms = [Term(text=word["text"], translation=word["translation"],
                           gender=word["gender"] if "gender" in word else None,
                           case=word["case"] if "case" in word else None,
                           word_type=word["word_type"] if "word_type" in word else None,
                           compound_id=word["compound_id"] if "compound_id" in word else None,
                           idiom_id=word["idiom_id"] if "idiom_id" in word else None,
                           kanjis=word["kanjis"] if "kanjis" in word else None,
                           hanzis=word["hanzis"] if "hanzis" in word else None,
                           note=word["note"] if "note" in word else None,
                           ) for word in response_json["sentence"]]
    sentence_compounds = []
    if "compounds" in response_json and len(response_json["compounds"]) > 0:
        sentence_compounds += [Compound(
            id=word["id"],
            text=word["text"],
            translation=word["translation"]
        ) for word in response_json["compounds"]]
    sentence_idioms = []
    if "idioms" in response_json and len(response_json["idioms"]) > 0:
        sentence_idioms += [Compound(
            id=word["id"],
            text=word["text"],
            translation=word["translation"]
        ) for word in response_json["idioms"]]
    return sentence_terms, sentence_compounds, sentence_idioms


def _calculate_sentence_translation_json(sentence: Term, from_lang, index):
    print(f"Getting word splits for sentence {index+1}")
    try:
        sentence_terms, sentence_compounds, sentence_idioms = _get_word_splits_and_translation_from_gpt(
            sentence, from_lang)
        transliterate_terms(sentence_terms, from_lang)

        legacy_terms_one_sentence = sentence_terms.copy()
        legacy_compounds_one_sentence = sentence_compounds.copy()
        legacy_idioms_one_sentence = sentence_idioms.copy()

        _add_position_to_terms(sentence.text, sentence_terms)
        sentence_translation_json = {
            "terms": [t.to_dict() for t in sentence_terms],
            "wholeSentence": sentence.to_dict(),
        }

        if sentence_compounds:
            sentence_translation_json["compounds"] = [
                c.__dict__ for c in sentence_compounds]
        if sentence_idioms:
            sentence_translation_json["idioms"] = [
                i.__dict__ for i in sentence_idioms]
        
        return sentence_translation_json, legacy_terms_one_sentence, legacy_compounds_one_sentence, legacy_idioms_one_sentence
    except Exception as e:
        print(f"Error getting word splits for sentence {index+1}. Moving on. Error: {e}")
        return None, None, None, None


def _calculate_sentence_by_sentence_translation_json(sentences: list[Term], from_lang) -> tuple[list[Term], list[Compound], list[Compound]]:
    sentence_translation_jsons = len(sentences)*[None]
    legacy_terms = len(sentences)*[None]
    legacy_compounds = len(sentences)*[None]
    legacy_idioms = len(sentences)*[None]
    # STEP 1: parallel: tuples = pool.map(_get_word_splits_and_translation_from_gpt(sentence, from_lang))
    # STEP 2 synch, process tuples

    with ThreadPoolExecutor(max_workers=10) as executor:
        #for index, sentence in enumerate(sentences):
        future_to_translation_json = {executor.submit(_calculate_sentence_translation_json, sentence, from_lang, index): 
                                      (sentence, from_lang, index) for index, sentence in enumerate(sentences)}
        for future in as_completed(future_to_translation_json):
            sentence, from_lang, index = future_to_translation_json[future]
            print(f"Got word splits for sentence {index+1}/{len(sentences)}")
            sentence_translation_json, legacy_terms_one_sentence, legacy_compounds_one_sentence, legacy_idioms_one_sentence = future.result()

            sentence_translation_jsons[index] = sentence_translation_json
            legacy_terms[index] = legacy_terms_one_sentence
            legacy_compounds[index] = legacy_compounds_one_sentence
            legacy_idioms[index] = legacy_idioms_one_sentence

    legacy_terms = list(itertools.chain.from_iterable(legacy_terms))
    legacy_compounds = list(itertools.chain.from_iterable(legacy_compounds))
    legacy_idioms = list(itertools.chain.from_iterable(legacy_idioms))
    return sentence_translation_jsons, legacy_terms, legacy_compounds, legacy_idioms


def get_translation_json(text, from_lang) -> dict:
    sentences: list[Term] = get_sentences(text)
    translate_sentences(sentences, from_lang, "en")
    transliterate_terms(sentences, from_lang)

    sentence_translation_jsons, legacy_word_groups, legacy_compounds, legacy_idioms = _calculate_sentence_by_sentence_translation_json(
        sentences, from_lang)
    # legacy:
    _add_position_to_terms(text, legacy_word_groups)

    return {
        "terms": [w.to_dict() for w in legacy_word_groups],
        "compounds": [c.__dict__ for c in legacy_compounds],
        "idioms": [i.__dict__ for i in legacy_idioms],
        "sentences": [s.to_dict() for s in sentences],
        "sentenceTranslationJsons": sentence_translation_jsons,
    }
