from google.cloud import translate

import os

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
