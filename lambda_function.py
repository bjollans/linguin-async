import json
from util.dummy import hello_world

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
        case _:
            response_body = hello_world()

    return {
        'statusCode': 200,
        'body': json.dumps(response_body)
    }


if __name__ == "__main__":
    args = sys.argv

    event = {'queryStringParameters': {'type': 'test'}}
    context = {}

    print(lambda_handler(event, context)['body'])