from dotenv import load_dotenv
load_dotenv()

from api import generate_audio
import json
from api.update_conversation import update_conversation
from api.update_conversations import update_conversations
from api.translate_story import translate_story
from util import db
from util.audio.audio_orchestrate import generate_audio_for_story

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
        case _:
            return {
                'statusCode': 400,
                'body': json.dumps("empty")
            }


if __name__ == "__main__":
    print("cbdcccab-18e4-437f-94f2-c3ed5e41df17 -- 1")
    generate_audio_for_story("cbdcccab-18e4-437f-94f2-c3ed5e41df17")
    print("29e9e3ec-8695-483f-bb11-420cacf2d599 -- 2")
    generate_audio_for_story("29e9e3ec-8695-483f-bb11-420cacf2d599")
    print("d0a04693-68a4-4acc-986e-ae7e9bca8ca3 -- 3")
    generate_audio_for_story("d0a04693-68a4-4acc-986e-ae7e9bca8ca3")
    print("63c2969e-cb07-4c03-b120-6732abc9731d -- 4")
    generate_audio_for_story("63c2969e-cb07-4c03-b120-6732abc9731d")
    print("726a0099-b102-4cff-ae31-603d29dddf6a -- 5")
    generate_audio_for_story("726a0099-b102-4cff-ae31-603d29dddf6a")
    print("4be18f13-ecfd-482d-8246-695cd61c2f33 -- 6")
    generate_audio_for_story("4be18f13-ecfd-482d-8246-695cd61c2f33")
    print("ed88f7d6-814b-4ad5-ac70-aaa72bb91de6 -- 7")
    generate_audio_for_story("ed88f7d6-814b-4ad5-ac70-aaa72bb91de6")
    print("2ddf9ff4-512a-4c5d-8209-9103a03f9ec6 -- 8")
    generate_audio_for_story("2ddf9ff4-512a-4c5d-8209-9103a03f9ec6")
    print("6d75347a-b66a-43ae-95b6-2ccb75b0c0ac -- 9")
    generate_audio_for_story("6d75347a-b66a-43ae-95b6-2ccb75b0c0ac")
    print("6d4bdbd9-fc5d-4f8f-8a73-9a5cea0fe060 -- 10")
    generate_audio_for_story("6d4bdbd9-fc5d-4f8f-8a73-9a5cea0fe060")
    print("ca506400-9214-400d-87bc-9a351ad56452 -- 11")
    generate_audio_for_story("ca506400-9214-400d-87bc-9a351ad56452")
    print("3f853634-1db1-4440-830a-84b7905f3815 -- 12")
    generate_audio_for_story("3f853634-1db1-4440-830a-84b7905f3815")
    print("eeea7d5c-2b32-4372-829e-ffa8204e22dc -- 13")
    generate_audio_for_story("eeea7d5c-2b32-4372-829e-ffa8204e22dc")
    print("2bbf42ec-3377-438e-a59e-8a8b19d71d6c -- 14")
    generate_audio_for_story("2bbf42ec-3377-438e-a59e-8a8b19d71d6c")
    print("00aa798e-6ea2-4b9a-8803-aa61e2849bf9 -- 15")
    generate_audio_for_story("00aa798e-6ea2-4b9a-8803-aa61e2849bf9")
    print("ade75287-d415-40bb-b031-96cdbe42d951 -- 16")
    generate_audio_for_story("ade75287-d415-40bb-b031-96cdbe42d951")
    print("ce0da421-5010-464b-815a-ff0aa5893187 -- 17")
    generate_audio_for_story("ce0da421-5010-464b-815a-ff0aa5893187")
    print("c9081dfd-9ae6-4ebd-bdf4-4df5970b6490 -- 18")
    generate_audio_for_story("c9081dfd-9ae6-4ebd-bdf4-4df5970b6490")
    print("6f0a53ea-c504-4071-9eba-08e960ff60a1 -- 19")
    generate_audio_for_story("6f0a53ea-c504-4071-9eba-08e960ff60a1")