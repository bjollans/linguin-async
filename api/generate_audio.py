from util.audio.audio_orchestrate import generate_audio_for_story, generate_audio_for_words_by_translation_json
from api.common_responses import success
import util.db as db

def generate_audio(query):
    story_id = query["id"]
    generate_audio_for_story(story_id)
    return success

def generate_audio_for_all_stories():
    stories = db.get_stories_without_audio()
    for i, story in enumerate(stories):
        print(f"Generating audio for {story['id']}; {i+1}/{len(stories)}")
        query = {"id": story["id"]}
        generate_audio(query)
        print(f"Generated for words in {story['id']}; {i+1}/{len(stories)}")
        generate_audio_for_words_by_translation_json(story["id"])
    return success

def generate_audio_for_all_words_in_story(query):
    story_id = query["id"]
    generate_audio_for_words_by_translation_json(story_id)
    return success
