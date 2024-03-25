from util.get_translation_json import get_translation_json
import util.db as db
from api.common_responses import success
from util.get_word_list import get_word_list_from_translation_json
from util.translation import proof_read_translation, translate_text

def translate_story(query):
    story_id = query["id"]
    story = db.get_story_by_id(story_id)
    target_language = query["targetLanguage"] if "targetLanguage" in query else story["targetLanguage"]
    story_translation = {}
    story_translation["targetLanguage"] = target_language
    if story["en"]:
        translated_text = translate_text(story["en"], "en", target_language)
        story_translation["content"] = proof_read_translation(story["en"],translated_text, target_language)
    translation_json = get_translation_json(story_translation["content"], target_language)
    story_translation["translationJson"] = translation_json
    story_translation["wordCount"] = len(translation_json["terms"])
    story_translation["storyId"] = story_id
    story_translation["wordsInStory"] = get_word_list_from_translation_json(translation_json)
    db.insert_story_translation(story_translation)
    return success

def translate_stories_without_translation():
    story_ids = db.get_story_ids_done_without_translation()
    for i, story_id in enumerate(story_ids):
        print(f"Translating {story_id}; {i+1}/{len(story_ids)}")
        translate_story({"id": story_id})
    return success