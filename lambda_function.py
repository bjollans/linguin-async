import json
from api.update_conversation import update_conversation
from api.update_conversations import update_conversations
from api.translate_story import translate_story
from util.audio.audio_orchestrate import text_to_audio_with_sentence_timestamps

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
        case 'translate_story':
            return translate_story(query)
        case _:
            return {
                'statusCode': 400,
                'body': json.dumps("empty")
            }


if __name__ == "__main__":
    #Move to top of file
    from dotenv import load_dotenv
    load_dotenv()

    text = """
एक समय की बात है, भारत के एक घने जंगल में एक चतुर सियार रहता था।
वह हमेशा भूखा रहता था और लगातार भोजन की तलाश में रहता था।
एक दिन, भोजन की तलाश करते हुए, वह भटक कर पास के एक गाँव में पहुँच गया।


जब वह बाहर आया तो सिर से पूंछ तक बिल्कुल नीला था।
उसने पास के एक तालाब में अपने प्रतिबिंब को देखा और अपना नया रूप देखकर आश्चर्यचकित रह गया।
"""
    lang = "hi"
    output_file = "my_test.mp3"
    timestamps = text_to_audio_with_sentence_timestamps(text, lang, output_file)
    print(timestamps)