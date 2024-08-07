from concurrent.futures import ThreadPoolExecutor, as_completed
from util.audio.concatenate import concatenate_and_save_mp3, get_time_stamps
from util.audio.generate import generate_audio_for_sentence, generate_audio_for_text
import util.db as db
import os


def _text_to_audio_with_sentence_timestamps(text, lang, output_file):
    generated_file_prefix = "narakeet"
    generated_files = generate_audio_for_text(text, lang, generated_file_prefix)
    concatenate_and_save_mp3(generated_files, output_file)
    sentence_timestamps = get_time_stamps(generated_files)
    return sentence_timestamps

def generate_audio_for_story_translation(story_translation_id):
    char_whitelist = set('abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ')

    story_translation = db.get_story_translation_by_id(story_translation_id)
    story_id = story_translation["storyId"]

    story = db.get_story_by_id(story_id)
    text = story_translation["content"]
    lang = story_translation["targetLanguage"]
    title = ''.join(filter(char_whitelist.__contains__, story["title"]))


    audio_file = f"/tmp/{title}.mp3"
    sentence_timestamps = _text_to_audio_with_sentence_timestamps(text, lang, audio_file)
    audio_url = db.upload_audio_to_bucket(audio_file, f"{title}.mp3")
    story_translation["audioUrl"] = audio_url
    story_translation["audioSentenceTimes"] = sentence_timestamps
    db.update_story_translation(story_translation)


def get_file_name_for_word(lang, word):
    return lang+ "-" + "-".join([str(ord(letter)) for letter in word])

_local_word_audio_cache=[]

def generate_audio_for_word(lang, word):
    if lang+'-'+word in _local_word_audio_cache:
        print(f"Audio for {word} already exists in local cache")
        return
    if db.file_exists(f"{get_file_name_for_word(lang, word)}.mp3", bucket="wordSound"):
        print(f"Audio for {word} already exists in bucket")
        _local_word_audio_cache.append(lang+'-'+word)
        return
    print(f"Generating audio for {word}")
    file_name = get_file_name_for_word(lang, word)
    audio_file = f"/tmp/{file_name}.mp3"
    generate_audio_for_sentence(word, lang, audio_file)
    try:
        db.upload_audio_to_bucket(audio_file, f"{file_name}.mp3", bucket="wordSound")
    except Exception as e:
        if "The resource already exists" in str(e):
            print(f"Audio for {word} already exists in bucket")
        else:
            raise e
    os.remove(audio_file)
    _local_word_audio_cache.append(word)


def generate_audio_for_words_by_translation_json(story_translation_id):
    story_translation = db.get_story_translation_by_id(story_translation_id)
    lang = story_translation["targetLanguage"]
    translation_json = story_translation["translationJson"]
    words_to_record = [term["text"] for term in translation_json["terms"]]

    with ThreadPoolExecutor(max_workers=10) as executor:
        for word in words_to_record:
            executor.submit(generate_audio_for_word, lang, word)