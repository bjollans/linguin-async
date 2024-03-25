from util.audio.audio_orchestrate import generate_audio_for_story_translation, generate_audio_for_words_by_translation_json
from api.common_responses import success
import util.db as db

def generate_audio(query):
    story_translation_id = query["id"]
    generate_audio_for_story_translation(story_translation_id)
    return success

def generate_audio_for_all_translations():
    story_translations = db.get_story_translations_without_audio()
    for i, story_translation in enumerate(story_translations):
        print(f"Generating audio for {story_translation['id']}; {i+1}/{len(story_translations)}")
        query = {"id": story_translation["id"]}
        generate_audio(query)
        print(f"Generated for words in {story_translation['id']}; {i+1}/{len(story_translations)}")
        generate_audio_for_words_by_translation_json(story_translation["id"])
    return success

def generate_audio_for_all_words_in_story(query):
    story_id = query["id"]
    generate_audio_for_words_by_translation_json(story_id)
    return success
