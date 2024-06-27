from collections import defaultdict, namedtuple
from dataclasses import asdict, dataclass
import json
from typing import List
import uuid

from devatrans import DevaTrans

from util.gpt.gpt import single_chat_completion
import util.gpt.word_operations as gpt
from util.translation import translate_text
from util.transliteration.el import get_greek_transliteration
from util.transliteration.hi import get_indic_transliteration
from util.transliteration.ja import get_japanese_transliteration
from util.transliteration.zh import get_chinese_transliteration
from util.vocab_db import VocabDB
from util.word_splitter import WordSplitter


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

    def to_dict(self):
        return asdict(self, dict_factory=lambda x: {k: v for (k, v) in x if v is not None})


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


def _get_gpt_word_splits_prompt(text: str) -> str:
    return f"""Given this sentence:
{text}

Give me the word wise translation (every single word, do not leave out any words).
Give word_type for every word.
Only give the "case" and "gender" where relevant.
If a word is part of a compound verb add it in the "compounds" section.
If a word is part of a correlative cojunction add it in the "compounds" section.
Add the "compound_id" to all words, that are part of the compound. Only add verbs to compound verbs.
If a word is part of an idiom or figure of speech, add it to the "idioms" section. Add the "idiom_id" to all words that are part of the idiom.
For the `translation` part, pretend the word or compound is standing alone. Return in json format like so (omit empty fields):
""" + '\'{"sentence":[ {"text": "untranslated word","translation": "translated word","word_type": "e.g. verb, postposition, particle","case":"case of the word", "gender": "gender of the word","compound_id": "id of the compound", "idiom_id":"id of the idiom"},...], "compounds": [{"id": "id of the compound","text": "untranslated compound", "translation": "translation of the compound"},...], "idioms": [{"id": "id of the idiom","text": "untranslated idiom", "translation": "translation of the idiom"},...]}\''


def _get_word_splits_and_translation_from_gpt(sentence):
    response_json = {}
    tries = 0
    while not "sentence" in response_json:
        tries += 1
        if tries > 5:
            raise Exception("Could not get word splits from gpt")
        prompt = _get_gpt_word_splits_prompt(sentence.text)
        response = single_chat_completion(
            prompt, type="json_object", max_tokens=2048, temperature=0, top_p=0.2)
        try:
            response_json = (json.loads(response))
        except json.decoder.JSONDecodeError:
            print("Could not parse json. Trying again.")
            continue
    sentence_terms = [Term(text=word["text"], translation=word["translation"],
                           gender=word["gender"] if "gender" in word else None,
                           case=word["case"] if "case" in word else None,
                           word_type=word["word_type"] if "word_type" in word else None,
                           compound_id=word["compound_id"] if "compound_id" in word else None,
                           idiom_id=word["idiom_id"] if "idiom_id" in word else None,
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
    remove_compounds_with_bad_amount_of_words(
        sentence_terms, sentence_compounds, sentence_idioms)
    return sentence_terms, sentence_compounds, sentence_idioms


def _calculate_sentence_by_sentence_translation_json(sentences: list[Term], from_lang) -> tuple[list[Term], list[Compound], list[Compound]]:
    sentence_translation_jsons = []
    legacy_terms = []
    legacy_compounds = []
    legacy_idioms = []
    for index, sentence in enumerate(sentences):
        print(f"Getting word splits for sentence {index+1}/{len(sentences)}")
        sentence_terms, sentence_compounds, sentence_idioms = _get_word_splits_and_translation_from_gpt(
            sentence)
        transliterate_terms(sentence_terms, from_lang)

        legacy_terms += sentence_terms.copy()
        legacy_compounds += sentence_compounds.copy()
        legacy_idioms += sentence_idioms.copy()

        _add_position_to_terms(sentence.text, sentence_terms)
        sentence_translation_jsons.append({
            "terms": [t.to_dict() for t in sentence_terms],
            "compounds": [c.__dict__ for c in sentence_compounds],
            "idioms": [i.__dict__ for i in sentence_idioms],
            "wholeSentence": sentence.to_dict(),
        })

    return sentence_translation_jsons, legacy_terms, legacy_compounds, legacy_idioms


def remove_compounds_with_bad_amount_of_words(terms, compounds, idioms):
    compound_id_count = defaultdict(lambda: 0)
    idiom_id_count = defaultdict(lambda: 0)
    for term in terms:
        if term.compound_id:
            compound_id_count[term.compound_id] += 1
        if term.idiom_id:
            idiom_id_count[term.idiom_id] += 1
    for term in terms:
        if term.compound_id and compound_id_count[term.compound_id] <= 1:
            term.compound_id = None
    for compound in compounds:
        if compound_id_count[compound.id] <= 1:
            compounds.remove(compound)
    for idiom in idioms:
        if idiom_id_count[idiom.id] <= 1:
            idioms.remove(idiom)


def get_translation_json(text, from_lang) -> dict:
    sentences: list[Term] = get_sentences(text)
    translate_sentences(sentences, from_lang, "en")
    transliterate_terms(sentences, from_lang)

    sentence_translation_jsons, legacy_word_groups, legacy_compounds, legacy_idioms = _calculate_sentence_by_sentence_translation_json(
        sentences, from_lang)
    # legacy:
    _add_position_to_terms(text, legacy_word_groups)

    return {
        "terms": [w.__dict__ for w in legacy_word_groups],
        "compounds": [c.__dict__ for c in legacy_compounds],
        "idioms": [i.__dict__ for i in legacy_idioms],
        "sentences": [s.__dict__ for s in sentences],
        "sentenceTranslationJsons": sentence_translation_jsons,
    }
