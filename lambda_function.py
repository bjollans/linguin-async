import json
from api.update_conversation import update_conversation
from api.update_conversations import update_conversations
from api.translate_story import translate_story

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
        case _:
            return {
                'statusCode': 400,
                'body': json.dumps("empty")
            }


if __name__ == "__main__":
    translate_story({"id": "dfecda7e-f6c1-4b2e-ae1b-857eca4a921f"})