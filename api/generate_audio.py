from util.audio.audio_orchestrate import generate_audio_for_story
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
        generate_audio({"id": story["id"]})
    return success