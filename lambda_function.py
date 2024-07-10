from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from api import generate_questions
from api.update_story_images import update_images_for_stories_without_images
from util import db
from util.audio.audio_orchestrate import generate_audio_for_story_translation, generate_audio_for_words_by_translation_json, get_file_name_for_word
from util.get_translation_json import get_translation_json
from util.translation import proof_read_translation
from util.validation.sentence_size import sentences_are_too_long
load_dotenv()

from util.story_generation.orchestrate import check_story_duplicates, generate_and_save_article, generate_and_save_articles, generate_and_save_known_fiction_story, generate_and_save_mini_story, generate_and_save_mini_story_by_committee, generate_and_save_summaries, generate_content_from_collection_name, generate_images_for_image_pending_stories, generate_one_round_of_content
from util.gpt.story_generation import generate_ideas_for_articles, generate_ideas_for_collections, generate_known_fiction_story, generate_mini_story, generate_mini_story_by_committee, generate_mini_story_with_image_jul_2024, generate_non_fiction_story
from api.generate_audio import generate_audio, generate_audio_for_all_translations, generate_audio_for_all_words_in_story
import json
from api.update_conversation import update_conversation
from api.update_conversations import update_conversations
from api.translate_story import translate_story, translate_stories_without_translation, translate_story_generate_audio_and_mark_as_new_default, update_translation_json_and_word_audio, update_translation_json_and_word_audio_by_language
from api.generate_questions import generate_questions_for_all_stories

required_args = ['type']

def validate_query(query):
    if not query:
        return False
    for arg in required_args:
        if arg not in query:
            return False
    return True


def lambda_handler(event, context):
    query = event['queryStringParameters']
    if not validate_query(query):
        return {
            'statusCode': 400,
            'body': json.dumps("User Error: Missing some arguments.")
        }

    match query['type'] if 'type' in query else None:
        case 'update_conversation':
            return update_conversation(query)
        case 'update_conversations':
            return update_conversations(query)
        case 'translate_story':
            return translate_story(query)
        case 'generate_audio':
            return generate_audio(query)
        case 'translate_stories_without_translation':
            return translate_stories_without_translation()
        case 'generate_audio_for_all_translations':
            return generate_audio_for_all_translations()
        case _:
            return {
                'statusCode': 400,
                'body': json.dumps("empty")
            }


if __name__ == "__main__":
    print("Done")