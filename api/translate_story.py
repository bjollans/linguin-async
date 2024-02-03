from util.get_translation_json import get_translation_json
import util.db as db
from api.common_responses import success
from util.get_word_list import get_word_list_from_translation_json
from util.translation import translate_text

def translate_story(query):
    story_id = query["id"]
    story = db.get_story_by_id(story_id)
    if story["en"]:
        story["content"] = translate_text(story["en"], "en", story["targetLanguage"])
    translation_json = get_translation_json(story["content"], story["targetLanguage"], story["translationLanguage"])
    story["translationJson"] = translation_json
    story["wordCount"] = len(story["content"].split(" "))
    image_title = story["title"].replace("'","")
    story["imageUrl"] = f"https://backend.linguin.co/storage/v1/object/public/storyImages/{image_title}.gif"
    story["previewImageUrl"] = f"https://backend.linguin.co/storage/v1/object/public/storyImages/{image_title}_preview.gif"
    story["wordsInStory"] = get_word_list_from_translation_json(translation_json)
    db.update_story(story)
    return success

def translate_stories_without_content():
    stories = db.get_stories_done_without_content()
    for i, story in enumerate(stories):
        print(f"Translating {story['id']}; {i+1}/{len(stories)}")
        translate_story({"id": story["id"]})
    return success