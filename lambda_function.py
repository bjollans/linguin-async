import json
from api.update_conversation import update_conversation
from api.update_conversations import update_conversations
from util.dummy import hello_world
import sys

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
        case _:
            return {
                'statusCode': 400,
                'body': json.dumps("empty")
            }


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    args = sys.argv

    event = {'queryStringParameters': {'type': 'update_conversations', 'id': '798e9ce7-f320-4dcb-9809-c8938c5ad127'}}
    context = {}

    print(lambda_handler(event, context)['body'])