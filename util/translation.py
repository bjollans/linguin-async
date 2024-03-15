from google.cloud import translate

import os

from util.gpt.gpt import single_chat_completion

_cache = {}
def translate_text(text, from_lang, to_lang):
    global _cache
    _cache_key = text + from_lang + to_lang
    if _cache_key not in _cache:
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
        _cache[_cache_key] = response.translations[0].translated_text
    return _cache[_cache_key]


def proof_read_translation(original_text, translated_text, to_lang):
    language_full_form = {
        "hi": "Hindi",
        "ja": "Japanese",
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
