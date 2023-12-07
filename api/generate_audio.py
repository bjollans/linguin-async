from util.audio.audio_orchestrate import generate_audio_for_story
from api.common_responses import success

def generate_audio(query):
    story_id = query["id"]
    generate_audio_for_story(story_id)
    return success