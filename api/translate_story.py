from util.audio.audio_orchestrate import generate_audio_for_story_translation, generate_audio_for_words_by_translation_json
from util.get_translation_json import get_translation_json
import util.db as db
from api.common_responses import success
from util.get_word_list import get_word_list_from_translation_json
from util.translation import fix_formatting, proof_read_translation, translate_text
from util.validation.sentence_size import sentences_are_too_long

def translate_story_generate_audio_and_mark_as_new_default(query):
    story_id = query["id"]
    print(f"Translating {story_id}")
    story_translation_id = translate_story(query)
    print(f"Generating audio for story translation {story_translation_id}")
    generate_audio_for_story_translation(story_translation_id)
    print(f"Generating audio for words in {story_translation_id}")
    generate_audio_for_words_by_translation_json(story_translation_id)
    print(f"Marking {story_translation_id} as new default translation for {story_id}")
    db.mark_story_translation_as_visible(story_translation_id)
    db.mark_other_story_translations_for_story_as_not_visible(story_translation_id, story_id)
    return success


def translate_story(query):
    tries_left = 3 if "tries_left" not in query else query["tries_left"]
    try:
        story_id = query["id"]
        story = db.get_story_by_id(story_id)
        target_language = query["targetLanguage"] if "targetLanguage" in query else story["targetLanguage"]
        story_translation = {}
        story_translation["targetLanguage"] = target_language
        if story["en"]:
            print(f"Translating complete story {story_id} from English to {target_language}")
            translated_text = translate_text(story["en"], "en", target_language)
            print(f"Proofreading story {story_id}")
            proofread_translated_text = proof_read_translation(story["en"],translated_text, target_language).replace("```\n","").replace("\n```","")
            print(f"Fixing formatting for story {story_id}")
            story_translation["content"] = fix_formatting(story["en"], proofread_translated_text).replace("```\n","").replace("\n```","")
            if sentences_are_too_long(story_translation["content"], target_language):
                raise Exception("Sentences too long")
        translation_json = get_translation_json(story_translation["content"], target_language)
        story_translation["translationJson"] = translation_json
        story_translation["wordCount"] = len(translation_json["terms"])
        story_translation["storyId"] = story_id
        story_translation["wordsInStory"] = get_word_list_from_translation_json(translation_json)
        story_translation_id = db.insert_story_translation(story_translation)
        return story_translation_id
    except Exception as e:
        print(f"Error translating story {story_id}. Trying again. Error: {e}")
        if tries_left > 0:
            return translate_story({"id": story_id, "targetLanguage": target_language, "tries_left": tries_left-1})
        else:
            raise e

def translate_stories_without_translation():
    story_ids = db.get_story_ids_done_without_translation()
    for i, story_id in enumerate(story_ids):
        print(f"Translating {story_id}; {i+1}/{len(story_ids)}")
        translate_story({"id": story_id})
    return success

def update_translation_json_and_word_audio_by_language(language):
    story_translation_ids = [x["id"] for x in db.get_story_tranlation_idsby_language(language)]
    for i, story_translation_id in enumerate(story_translation_ids):
        print(f"Translating {story_translation_id}; {i+1}/{len(story_translation_ids)}")
        update_translation_json_and_word_audio({"id": story_translation_id, "targetLanguage": language})


def update_translation_json_and_word_audio(query):
    story_translation_id = query["id"]
    target_language = query["targetLanguage"]
    story_translation = db.get_story_translation_by_id(story_translation_id)
    translation_json = get_translation_json(story_translation["content"], target_language)
    story_translation["wordsInStory"] = get_word_list_from_translation_json(translation_json)
    story_translation["translationJson"] = translation_json
    db.update_story_translation(story_translation)
    # print(f"Generating audio for {story_translation_id}")
    # generate_audio_for_story_translation(story_translation_id)
    print(f"Generating for words in {story_translation_id}")
    generate_audio_for_words_by_translation_json(story_translation["id"])
    return success