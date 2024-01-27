from util.audio.concatenate import concatenate_and_save_mp3, get_time_stamps
from util.audio.generate import generate_audio_for_sentence, generate_audio_for_text
import util.db as db


def _text_to_audio_with_sentence_timestamps(text, lang, output_file):
    generated_file_prefix = "narakeet"
    generated_files = generate_audio_for_text(text, lang, generated_file_prefix)
    concatenate_and_save_mp3(generated_files, output_file)
    sentence_timestamps = get_time_stamps(generated_files)
    return sentence_timestamps

def generate_audio_for_story(story_id):
    char_whitelist = set('abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ')

    story = db.get_story_by_id(story_id)
    text = story["content"]
    lang = story["targetLanguage"]
    title = ''.join(filter(char_whitelist.__contains__, story["title"]))


    audio_file = f"/tmp/{title}.mp3"
    sentence_timestamps = _text_to_audio_with_sentence_timestamps(text, lang, audio_file)
    audio_url = db.upload_audio_to_bucket(audio_file, f"{title}.mp3")
    story["audioUrl"] = audio_url
    story["audioSentenceTimes"] = sentence_timestamps
    db.update_story(story)


def get_file_name_for_word(word):
    return "-".join([str(ord(letter)) for letter in word])

def generate_audio_for_words_by_translation_json(story_id):
    story = db.get_story_by_id(story_id)
    lang = story["targetLanguage"]
    translation_json = story["translationJson"]
    words_to_record = [term["text"] for term in translation_json["terms"]]

    for word in words_to_record:
        if db.file_exists(f"{get_file_name_for_word(word)}.mp3", bucket="wordSound"):
            print(f"Audio for {word} already exists")
            continue
        print(f"Generating audio for {word}")
        file_name = get_file_name_for_word(word)
        audio_file = f"/tmp/{file_name}.mp3"
        generate_audio_for_sentence(word, lang, audio_file)
        db.upload_audio_to_bucket(audio_file, f"{file_name}.mp3", bucket="wordSound")