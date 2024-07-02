import json
from util.gpt.gpt import single_chat_completion


def get_gpt_word_splits_prompt(text: str, from_lang: str) -> str:
    if from_lang == "hi":
        return f"""Given this sentence:
{text}

Give me the word wise translation (every single word).
Give word_type for every word.
Give the gender for nouns.
Mention if a noun is in the oblique case.

If a word is part of a compound verb or phrasal verb add it in the "compounds" section.
If a word is part of a correlative add it in the "compounds" section.
Add the "compound_id" to all words, that are part of the compound.

If a word is part of a fixed phrase, proverb or idiom add it in the "idioms" section.
Add the "idiom_id" to all words that are part of the idiom.

For the dictionary_translation, imagine the word is standing alone.
Return in json format like so (omit empty fields):
""" + '\'{"sentence":[ {"text": "untranslated word","dictionary_translation": "usual dictionary translation","context_translation": "translation in this sentence","word_type": "e.g. verb, postposition, particle","case":"\'oblique\' if it is a noun in oblique case, else empty", "gender": "gender of the noun","compound_id": "id of the compound", "idiom_id":"id of the idiom"},...], "compounds": [{"id": "id of the compound","text": "untranslated compound", "translation": "translation of the compound"},...], "idioms": [{"id": "id of the idiom","text": "untranslated idiom", "translation": "translation of the idiom"},...]}\''


def get_gpt_word_splits(text: str, from_lang: str) -> str:
    prompt = get_gpt_word_splits_prompt(text, from_lang)
    tries = 0
    result_json = {}
    while not "sentence" in result_json:
        tries += 1
        if tries > 5:
            raise Exception("Could not get word splits from gpt")
        response = single_chat_completion(
            prompt, type="json_object", max_tokens=2048, temperature=0, top_p=0.2)
        try:
            result_json = (json.loads(response))
        except json.decoder.JSONDecodeError:
            print("Could not parse json. Trying again.")
            continue
    clean_result_json(result_json, from_lang)
    return result_json


def clean_result_json(result_json,from_lang):
    if from_lang == "hi":
        for entry in result_json["sentence"]:
            entry["translation"] = entry.pop("dictionary_translation")
            if entry["translation"] == entry["context_translation"]:
                del entry["context_translation"]