from util.get_translation_json import get_translation_json
import util.db as db
from api.common_responses import success

def translate_story(query):
    story_id = query["id"]
    story = db.get_story_by_id(story_id)
    story["translationJson"] = get_translation_json(story["content"], story["targetLanguage"], story["translationLanguage"])
    db.update_story(story)
    return success