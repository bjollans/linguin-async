from util import db


def get_word_list_from_story_id(story_id):
    story = db.get_story_by_id(story_id)
    return get_word_list_from_translation_json(story["translationJson"])

def get_word_list_from_translation_json(translation_json) -> list[str]:
    if not translation_json:
        return []
    word_list = set()
    for word_group in translation_json["terms"]:
        word_list.add(word_group["text"])
    return list(word_list)

def insert_word_list_for_story_id(story_id):
    story = db.get_story_by_id(story_id)
    translation_json = story["translationJson"]
    story["wordsInStory"] = get_word_list_from_translation_json(translation_json)
    db.update_story(story)

def insert_word_list_for_all_stories():
    stories = db.get_all_stories()
    for i, story in enumerate(stories):
        print(f"Inserting word list for {story['id']}; {i+1}/{len(stories)}")
        insert_word_list_for_story_id(story["id"])