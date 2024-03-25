from google.cloud import translate
import deepl

import os

from util.gpt.gpt import single_chat_completion

auth_key = os.environ.get("DEEPL_AUTH_KEY")
deepl_translator = deepl.Translator(auth_key)

deepl_languages = [
    "de","zh","el","es","fr","it","ja","nl","pl","pt","ru","tr"
]


_cache = {}
def translate_text(text, from_lang, to_lang):
    global _cache
    _cache_key = text + from_lang + to_lang
    if _cache_key not in _cache:
        _cache[_cache_key] = _deepl_translate(text, from_lang, to_lang) if to_lang.lower() in deepl_languages or from_lang.lower() in deepl_languages else _google_translate(text, from_lang, to_lang)
    return _cache[_cache_key]


def _deepl_translate(text, from_lang, to_lang):
    print("Using Deepl")
    result = deepl_translator.translate_text(text, target_lang="en-us" if to_lang=="en" else to_lang, source_lang=from_lang)
    return result.text


def _google_translate(text, from_lang, to_lang):
    print("Using Google Translate")
    project_id = os.environ.get("GOOGLE_PROJECT_ID")
    client = translate.TranslationServiceClient()
    location = "global"
    parent = f"projects/{project_id}/locations/{location}"
    response = client.translate_text(
        request={
            "parent": parent,
            "contents": [text],
            "mime_type": "text/plain",
            "source_language_code": from_lang,
            "target_language_code": to_lang
        }
    )
    return response.translations[0].translated_text


def proof_read_translation(original_text, translated_text, to_lang):
    language_full_form = {
        "hi": "Hindi",
        "ja": "Japanese",
        "el": "Greek",
        "zh": "Chinese",
        "de": "German",
    }
    prompt = f"""
I have the following story:
```
{original_text}
```
With the following {language_full_form[to_lang]} translation:
```
{translated_text}
```

The story is meant for language learners. Please proof read the {language_full_form[to_lang]} version and correct any mistakes you find. Please also replace words that are not commonly used in spoken {language_full_form[to_lang]}.

Just give me the proof read version of the story, without commentary.
"""
    return single_chat_completion(prompt)
