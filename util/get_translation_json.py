from collections import defaultdict, namedtuple
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


class Term:
    def __init__(self,
                 text,
                 position=-1,
                 translation=None,
                 transliteration=None,
                 case=None,
                 word_type=None,
                 gender=None,
                 compound_id=None,
                 idiom_id=None,
                 ):
        self.text = text
        self.position = position
        self.translation = translation
        if transliteration: self.transliteration = transliteration
        if compound_id: self.compound_id = compound_id
        if idiom_id: self.idiom_id = idiom_id
        if case: self.case = case
        if word_type: self.word_type = word_type
        if gender: self.gender = gender


class Compound:
    def __init__(self,
                 id,
                 text,
                 translation=None,
                 ):
        self.id = id
        self.text = text
        self.translation = translation


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


def _get_word_splits_and_translation_from_gpt(sentences: list[Term]) -> tuple[list[Term], list[Compound], list[Compound]]:
    terms = []
    compounds = []
    idioms = []
    for sentence in sentences:
        print(f"Getting word splits for sentence {
              sentences.index(sentence)+1}/{len(sentences)}")
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
        compound_uuids = get_list_of_uuids(len(response_json["compounds"]) + 1) if "compounds" in response_json else []
        print(f"compound_uuids: {compound_uuids}")
        idiom_uuids = get_list_of_uuids(len(response_json["idioms"]) + 1) if "idioms" in response_json else []
        terms += [Term(text=word["text"], translation=word["translation"],
                       gender=word["gender"] if "gender" in word else None,
                       case=word["case"] if "case" in word else None,
                       word_type=word["word_type"] if "word_type" in word else None,
                       compound_id=compound_uuids[int(word["compound_id"])] if "compound_id" in word else None,
                       idiom_id=idiom_uuids[int(word["idiom_id"])] if "idiom_id" in word else None,
                       ) for word in response_json["sentence"]]
        if "compounds" in response_json and len(response_json["compounds"]) > 0:
            compounds += [Compound(
                id=compound_uuids[int(word["id"])],
                text=word["text"],
                translation=word["translation"]
            ) for word in response_json["compounds"]]
        if "idioms" in response_json and len(response_json["idioms"]) > 0:
            idioms += [Compound(
                id=idiom_uuids[int(word["id"])],
                text=word["text"],
                translation=word["translation"]
            ) for word in response_json["idioms"]]
        remove_compounds_with_bad_amount_of_words(terms, compounds, idioms)
    return terms, compounds, idioms

def remove_compounds_with_bad_amount_of_words(terms, compounds, idioms):
    compound_id_count = defaultdict(lambda: 0)
    idiom_id_count = defaultdict(lambda: 0)
    for term in terms:
        if term.compound_id: compound_id_count[term.compound_id] += 1
        if term.idiom_id: idiom_id_count[term.idiom_id] += 1
    for term in terms:
        if term.compound_id and compound_id_count[term.compound_id] <= 1:
            terms.remove(term)
    for compound in compounds:
        if compound_id_count[compound.id] <= 1:
            compounds.remove(compound)
    for idiom in idioms:
        if idiom_id_count[idiom.id] <= 1:
            idioms.remove(idiom)

def get_list_of_uuids(length: int) -> List[str]:
    return [str(uuid.uuid4()) for i in range(length)]


def get_translation_json(text, from_lang) -> dict:
    sentences: list[Term] = get_sentences(text)
    translate_sentences(sentences, from_lang, "en")

    word_groups, compounds, idioms = _get_word_splits_and_translation_from_gpt(
        sentences)
    _add_position_to_terms(text, word_groups)

    transliterate_terms(word_groups, from_lang)
    transliterate_terms(sentences, from_lang)

    return {
        "terms": [w.__dict__ for w in word_groups],
        "compounds": [c.__dict__ for c in compounds],
        "idioms": [i.__dict__ for i in idioms],
        "sentences": [s.__dict__ for s in sentences],
    }
