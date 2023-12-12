from util.audio.concatenate import concatenate_and_save_mp3, get_time_stamps
from util.audio.generate import generate_audio_for_text
import util.db as db


def _text_to_audio_with_sentence_timestamps(text, lang, output_file):
    generated_file_prefix = "narakeet"
    generated_files = generate_audio_for_text(text, lang, generated_file_prefix)
    concatenate_and_save_mp3(generated_files, output_file)
    sentence_timestamps = get_time_stamps(generated_files)
    return sentence_timestamps

def generate_audio_for_story(story_id):
    story = db.get_story_by_id(story_id)
    text = story["content"]
    lang = story["targetLanguage"]
    title = story["title"]

    audio_file = f"/tmp/{title}.mp3"
    sentence_timestamps = _text_to_audio_with_sentence_timestamps(text, lang, audio_file)
    audio_url = db.upload_audio_to_bucket(audio_file, f"{title}.mp3")
    story["audioUrl"] = audio_url
    story["audioSentenceTimes"] = sentence_timestamps
    db.update_story(story)