from google.cloud import translate
import os

def translate_text(text, from_lang, to_lang):
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
            "target_language_code": to_lang,
        }
    )
    return response.translations[0].translated_text
