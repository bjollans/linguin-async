from dotenv import load_dotenv
load_dotenv()

from api.generate_audio import generate_audio, generate_audio_for_all_stories
import json
from api.update_conversation import update_conversation
from api.update_conversations import update_conversations
from api.translate_story import translate_story, translate_stories_without_content
from util import db

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
        case 'translate_stories_without_content':
            return translate_stories_without_content()
        case 'generate_audio_for_all_stories':
            return generate_audio_for_all_stories()
        case _:
            return {
                'statusCode': 400,
                'body': json.dumps("empty")
            }


if __name__ == "__main__":
    translate_stories_without_content()
    generate_audio_for_all_stories()