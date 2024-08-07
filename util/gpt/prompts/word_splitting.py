from collections import defaultdict
import json
import re
from util.gpt.gpt import single_chat_completion


def get_gpt_word_splits_prompt(text: str, from_lang: str) -> str:
    if from_lang == "hi":
        return f"""Given this sentence:
{text}

Give me the word wise translation (every single word).
Give word_type for every word.
Give the gender for nouns.
Mention if a noun is in the oblique case.
For all postpositions, add their function in this context and how they change the meaning of the words around them. Use simple language (4th grade reading level).

If a word is part of a compound verb or phrasal verb add it in the "compounds" section.
If a word is part of a correlative add its smallest unit in the "compounds" section.
Add the "compound_id" to all words, that are part of the compound.

If a word is part of a proverb or idiom add it in the "phrases" section.
Add the "phrase_id" to all words that are part of the phrase.

For the dictionary_translation, imagine the word is standing alone.
Return in json format like so (omit empty fields). Do "phrases" first, then do the "sentence" part. Do the "compounds" part last. :
""" + '\'{ "phrases": [{"id": "id of the phrase","text": "untranslated phrase", "translation": "translation of the phrase"},...], "sentence":[ {"text": "untranslated word","dictionary_translation": "usual dictionary translation","context_translation": "function in this sentence","word_type": "e.g. verb, postposition, particle","case":"\'oblique\' if it is a noun in oblique case, else empty", "gender": "gender of the noun","function":"function of a postposition. Start with \'in this context it...\'","compound_id": "id of the compound", "phrase_id":"id of the phrase"},...], "compounds": [{"id": "id of the compound","text": "untranslated compound", "translation": "translation of the compound"},...] }\''

    if from_lang == "ja":
        return f"""Given this sentence:
{text}

Give me the word wise translation (every single word). Translate every word only once.
Give word_type for every word. For adjectives include if they are ii- or na-adjectives
Do not split auxiliary adjectives off of the words they are attached to, or off of each other. Do not split the ending off a verb in the past tense.
Do not split the continuative form (verb + て)!!
Do not split the continuative form (verb + て)!!
Split auxiliary verbs off.

If two or more words make up a compound verb add it in the "compounds" section.
If a word has one or more auxiliary adjective attached, add this in the "compounds" section.
A particle plus another word can never be a compound!
Add the "compound_id" to all words, that are part of the compound.

If a word is written in kanjis, add them to the "kanjis" list with most common on readings and kun readings and most common meanings.

For the dictionary_translation, imagine the word is standing alone.
Return in json format like so (omit empty fields):
""" + '\'{"sentence":[ {"text": "untranslated word","translation": "translated word","word_type": "e.g. verb, postposition, particle,ii-adjective,na-adjective","compound_id": "id of the compound", "kanjis":[{"text":"kanji written","on":"most common on readings","kun":"most common kun readings","meaning":"most common meanings"},...]},...], "compounds": [{"id": "id of the compound","text": "untranslated compound", "translation": "translation of the compound"},...]}\''

    if from_lang == "de" or from_lang == "el":
        return f"""Given this sentence:
{text}

Give me the word wise translation (every single word). Do not split words.
Give word_type for every word.
Give the gender for nouns. If a noun is in plural, give the gender as if it was in singular.
Give the case for nouns, articles and adjectives.

If there is a separable verb construction, add it in the "separable_verbs" section.
Add the "separable_verb_id" to all parts of the separable verb construction.

If there is a common phrase or idiom, add it in the "phrases" section.
Add the "phrase_id" to all parts of the phrase.

Return in json format like so (omit empty fields). Do "phrases" first, then do "separable_verbs". Do the "sentence" part last. (for every single word in "{text}", without splitting any words):
""" + '\'{"phrases": [{"id": "id of the phrase","text": "untranslated phrase", "translation": "translation of the phrase"},...], {"separable_verbs": [{"id": "id of the separable verb","text": "untranslated separable verb", "translation": "translation of the separable verb"},...], "sentence":[ {"text": "untranslated word","translation": "translated word","word_type": "e.g. verb, adjective, noun","gender": "masculine/feminine/neuter","case":"dative/accusative/nominative/genitive","separable_verb_id": "id of the separable verb","phrase_id": "id of the phrase"},...]}\''

    if from_lang == "zh":
        return f"""Given this sentence:
{text}

Give me the word wise translation (every single word).
Give word_type for every word. For adjectives include if they are ii- or na-adjectives
Split auxiliary adjectives off of the words they are attached to.

If two or more words make up a compound verb add it in the "compounds" section.
If a word has one or more auxiliary adjective attached, add this in the "compounds" section.
A particle plus another word can never be a compound!
Add the "compound_id" to all words, that are part of the compound.

If a word is made up of multiple characters, add them in hanzis. Do not do this for words with only one character!!

For the dictionary_translation, imagine the word is standing alone.
Return in json format like so (omit empty fields):
""" + '\'{"sentence":[ {"text": "untranslated word","translation": "translated word","word_type": "e.g. verb, noun","compound_id": "id of the compound", "hanzis":[{"text":"hanzi 1 written","meaning":"meaning of the hanzi alone"}, ...]},...], "compounds": [{"id": "id of the compound","text": "untranslated compound", "translation": "translation of the compound"},...]}\''


def get_gpt_word_splits(text: str, from_lang: str) -> str:
    prompt = get_gpt_word_splits_prompt(text, from_lang)
    tries = 0
    result_json = {}
    while not "sentence" in result_json:
        tries += 1
        if tries > 5:
            raise Exception("Could not get word splits from gpt")
        response = single_chat_completion(
            prompt, type="json_object", max_tokens=4096, temperature=0, top_p=0)
        try:
            result_json = (json.loads(response))
        except json.decoder.JSONDecodeError:
            print(f"Could not parse json {response}. Trying again.")
            continue
        except Exception as e:
            print(f"Error getting word splits from gpt: {e}")
            continue
    clean_result_json(text, result_json, from_lang)
    return result_json


def clean_result_json(text, result_json, from_lang):
    if from_lang == "hi":
        for entry in result_json["sentence"]:
            entry["translation"] = entry.pop("dictionary_translation")
            if "context_translation" in entry and entry["translation"] == entry["context_translation"]:
                del entry["context_translation"]
            if "function" in entry:
                entry["note"] = entry.pop("function").lower().replace("in this context it ", "")
        merge_properties_into_compounds(["phrase"], result_json)
        allow_list_property("case", ["oblique"], result_json)
    if from_lang == "ja":
        remove_non_existant_kanjis(text, result_json)
        remove_non_kanjis(text, result_json)
    if from_lang == "de":
        merge_properties_into_compounds(["phrase","separable_verb"], result_json)
        allow_list_property(
            "gender", ["masculine", "feminine", "neuter"], result_json)
        allow_list_property(
            "case", ["accusative", "dative", "nominative", "genitive"], result_json)
    remove_words_not_in_sentence(text, result_json)
    remove_compounds_with_one_or_less_words_or_compounds(result_json)


def rename_property(old_name, new_name, result_json):
    for entry in result_json["sentence"]:
        if old_name in entry:
            entry[new_name] = entry.pop(old_name)


def merge_properties_into_compounds(property_names, result_json):
    # first properties take priority
    property_names.reverse()
    for index, property_name in enumerate(property_names):
        anti_collision_id_addition = (index * '00')
        for entry in result_json["sentence"]:
            if f"{property_name}_id" in entry:
                entry["compound_id"] = entry.pop(f"{property_name}_id") + anti_collision_id_addition
        property_name_plural = f"{property_name}s"
        if property_name_plural in result_json:
            for entry in result_json[property_name_plural]:
                entry["id"] += anti_collision_id_addition
            if "compounds" in result_json:
                result_json["compounds"] += result_json[property_name_plural]
            else:
                result_json["compounds"] = result_json[property_name_plural]


def allow_list_property(property_name, allow_list, result_json):
    for entry in result_json["sentence"]:
        if property_name in entry and entry[property_name] not in allow_list:
            del entry[property_name]


def remove_non_existant_kanjis(text, result_json):
    for entry in result_json["sentence"]:
        if not "kanjis" in entry:
            continue
        for i in range(len(entry["kanjis"])-1, -1, -1):
            actual_kanji = entry["kanjis"][i]["text"]
            if not actual_kanji in text:
                del entry["kanjis"][i]
        if len(entry["kanjis"]) == 0:
            del entry["kanjis"]


def remove_non_kanji(text):
    # Regular expression to match non-Kanji characters
    pattern = r'[^\u4e00-\u9faf\u3400-\u4dbf]'
    # Replace non-Kanji characters with empty string
    return re.sub(pattern, '', text)


def remove_non_kanjis(text, result_json):
    for entry in result_json["sentence"]:
        if not "kanjis" in entry:
            continue
        for i in range(len(entry["kanjis"])-1, -1, -1):
            actual_kanji = entry["kanjis"][i]["text"]
            entry["kanjis"][i]["text"] = remove_non_kanji(actual_kanji)
            if len(entry["kanjis"][i]["text"]) == 0:
                del entry["kanjis"][i]


def remove_words_not_in_sentence(text, result_json):
    for i in range(len(result_json["sentence"])-1, -1, -1):
        if result_json["sentence"][i]["text"] not in text:
            del result_json["sentence"][i]


def remove_compounds_with_one_or_less_words_or_compounds(result_json):
    compound_id_count = defaultdict(lambda: 0)
    idiom_id_count = defaultdict(lambda: 0)
    terms = result_json["sentence"]
    compounds = result_json["compounds"] if "compounds" in result_json else []
    idioms = result_json["idioms"] if "idioms" in result_json else []
    for term in terms:
        if "compound_id" in term:
            compound_id_count[term["compound_id"]] += 1
        if "idiom_id" in term:
            idiom_id_count[term["idiom_id"]] += 1
    for term in terms:
        if "compound_id" in term and compound_id_count[term["compound_id"]] <= 1:
            del term["compound_id"]
    for term in terms:
        if "idiom_id" in term and idiom_id_count[term["idiom_id"]] <= 1:
            del term["idiom_id"]
    for i in range(len(compounds)-1, -1, -1):
        if compound_id_count[compounds[i]["id"]] <= 1:
            compounds.remove(compounds[i])
    for i in range(len(idioms)-1, -1, -1):
        if idiom_id_count[idioms[i]["id"]] <= 1:
            idioms.remove(idioms[i])


def remove_compounds_that_are_same_as_one_word(result_json):
    if "compounds" not in result_json:
        return
    term_strs = [x["text"] for x in result_json["sentence"]]
    result_json["compounds"] = [
        x for x in result_json["compounds"] if x["text"] not in term_strs]
    if len(result_json["compounds"]) == 0:
        del result_json["compounds"]
    remove_compounds_with_one_or_less_words_or_compounds(result_json)
