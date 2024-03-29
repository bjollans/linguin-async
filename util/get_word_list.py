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
    story = add_word_list_to_story(story)
    db.update_story(story)

def add_word_list_to_story(story):
    translation_json = story["translationJson"]
    story["wordsInStory"] = get_word_list_from_translation_json(translation_json)
    return story

def insert_word_list_for_all_stories():
    stories = db.get_all_stories()
    for i, story in enumerate(stories):
        print(f"Inserting word list for {story['id']}; {i+1}/{len(stories)}")
        insert_word_list_for_story_id(story["id"])


def get_word_list_for_user_id(user_id):
    stories = db.get_stories_read_by_user(user_id)
    word_list = set()
    for story in stories:
        word_list.update(story["wordsInStory"])
    return list(word_list)


def refresh_user_read_statistics():
    user_ids = db.get_users_who_have_read_any_story()
    for i, user_id in enumerate(user_ids):
        print(f"Refreshing user read statistics for {user_id}; {i+1}/{len(user_ids)}")
        word_list = get_word_list_for_user_id(user_id)
        db.upsert_user_read_statistics(user_id, word_list)