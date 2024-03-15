from dotenv import load_dotenv
from api import generate_questions
from util.audio.audio_orchestrate import generate_audio_for_words_by_translation_json

from util.translation import proof_read_translation
load_dotenv()

from util.story_generation.orchestrate import generate_and_save_mini_story, generate_content_from_collection_name, generate_images_for_image_pending_stories, generate_one_round_of_content
from util.gpt.story_generation import generate_ideas_for_collections
from api.generate_audio import generate_audio, generate_audio_for_all_stories, generate_audio_for_all_words_in_story
import json
from api.update_conversation import update_conversation
from api.update_conversations import update_conversations
from api.translate_story import translate_story, translate_stories_without_content
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
    #generate_and_save_mini_story("ja")
    #translate_story({"id": "b96a54b1-bd7e-49c8-b3c3-08125397a9b2"})
    #generate_audio({"id": "b96a54b1-bd7e-49c8-b3c3-08125397a9b2"})


    #generate_one_round_of_content()
    #generate_images_for_image_pending_stories()

    #translate_stories_without_content()
    #generate_audio_for_all_stories()
    #generate_questions_for_all_stories()

    #stories = [
    ##    #"00aa798e-6ea2-4b9a-8803-aa61e2849bf9","09b1b19d-1ce8-4882-8224-2c21626b644c","0bc2267c-ea7a-4537-adcf-01003c5d84ef","0ce0824a-a884-4d94-bb57-4c3ae3ac8740","0d34b52e-e513-4c02-ac88-23c07aa599e2","1015fc67-e7db-4bb5-80f4-b39040dc6294","2119621f-536c-4417-8684-592de874c1cc",
    ##    #"2445d103-b86d-4520-9798-145a0d77927d","2526bfbd-bc60-4970-8a9c-3f869d93a159","29e9e3ec-8695-483f-bb11-420cacf2d599","2bbf42ec-3377-438e-a59e-8a8b19d71d6c","2c85bbc2-da62-4d7b-8e5a-14d81a43e3f5",
    ##    #"2ddf9ff4-512a-4c5d-8209-9103a03f9ec6","2e4c43d1-3561-4c16-ac78-b973e20a3d22","35bc6171-65fa-47cf-a01d-b6266e963482",
    #     #"3d196c9d-12d4-4dcd-abc4-5a32b047110c","3f853634-1db1-4440-830a-84b7905f3815","400e3f3c-eb23-4d92-af86-760fd0698961","42002d52-2852-4800-b670-af3dc877d158","4755d3b6-cbd3-4908-a5c4-dc5a76c132fa","4be18f13-ecfd-482d-8246-695cd61c2f33","4c7360e1-bd6b-4b8f-8b01-6389ab884fe9","4c876a32-a568-485d-987f-62843d04340b","53133121-34e5-41b0-b0fd-6a4f6c742220",
    #    "53fd403d-d054-448b-99b7-321aeb8a05b8","58195760-95c3-4e01-9b57-feae58df57a7","5a6fe41f-7038-4f62-8ab0-81524ad295a6","63c2969e-cb07-4c03-b120-6732abc9731d","63d75b8a-d20d-46f3-820f-a794c08ff004","65bb806c-c75e-43ca-b447-8ee72b58e54a","6a0b9b06-5dfb-42b6-b0c9-248fe8d89d64","6d4bdbd9-fc5d-4f8f-8a73-9a5cea0fe060","6d723350-56f1-4eea-9022-7b2c60abd7bb","6d75347a-b66a-43ae-95b6-2ccb75b0c0ac","6f0a53ea-c504-4071-9eba-08e960ff60a1","7073c52c-e453-4084-be4e-e874c88eceaa","71003e81-da19-4307-be39-df010590ee88","726a0099-b102-4cff-ae31-603d29dddf6a","72cfd064-0646-48d4-8591-e6e813217040","7c87d286-1caa-48c2-b89f-d2d861679b03","7d58a256-0684-4904-8da4-6bfb7ab8f155","7f7f87b3-e0f1-468d-8d1a-4486214f7b1e","7fc32ab1-c1fd-4cea-8172-59e746d9ec31","800c9cee-9739-4c62-b890-8d40423b631e","8490b028-9612-4b45-85c6-7a00fcb60290","8749aa74-dc1b-42cb-a432-6f73b3402031","88b53ebc-e685-4326-85f1-a6ba3efa2b64","90f15697-5a43-4ef4-b6e3-df5713692333","9213b165-2fc6-4fd4-9b68-67ad72fdc6d4","94a1f4fa-1c63-4c52-8bdf-22930ed555b2","9976fe88-8a39-4945-8cbe-83001b6a16f7","99c1937c-f3b7-4c22-a10f-0e300097dba3","9a9e78af-8c7d-40fc-9366-f2c36748f030","9dece4de-3136-4ecd-9333-f7a6877651f8","9e451a1f-424e-4568-b520-e2a7112a0e4f","ade75287-d415-40bb-b031-96cdbe42d951","adff4fae-9d53-4caa-beaf-c9e16cb53607","ae5dd877-4472-406a-a75d-349f64d1b89e","b32c647c-eae3-4daa-9c03-68ac42f82c38","b362603c-581f-452a-8762-100ec7e2ec1b","bb93c824-c24a-44be-82b7-12f68bf9b7cb","c78fab55-34fc-4553-a5a6-9fd445fc7a6e","c9081dfd-9ae6-4ebd-bdf4-4df5970b6490","c9aa959a-bb11-4bff-ad2a-dd907263442e","ca506400-9214-400d-87bc-9a351ad56452","cbdcccab-18e4-437f-94f2-c3ed5e41df17","cda14a5a-fd53-4714-9921-a9640870cec0","ce0da421-5010-464b-815a-ff0aa5893187","d02258d7-e59c-4c5a-9c08-a627187ab6ae","d0a04693-68a4-4acc-986e-ae7e9bca8ca3","d2769a03-a1d7-4d9e-924c-00582da64152","d2993ece-8f10-4abe-92c1-6a13f8399afa","d3471339-891c-4d9e-9431-4dd2c6bbcf2e","d5a2ed6e-993d-46dd-b1d2-72488e7f2e2b","d7bffbae-49b4-4081-a0e3-719180e0f64b","dde5cf7b-ab2c-4170-b600-4a2e6c93ac36","e0a1569e-3ee7-41ac-9e34-640fd5cd063e","e2ebcb12-7141-4941-838e-7e8ffedda979","e6316e6c-7d13-4c87-80f8-c647809cd80a","e8078f37-9f19-4bbb-a4b6-de784c6350c1","ed88f7d6-814b-4ad5-ac70-aaa72bb91de6","eeea7d5c-2b32-4372-829e-ffa8204e22dc","f3918290-9277-43e5-a6aa-a69c1b048cb8","f61ec46c-4044-47dd-8b66-bc2e67404603","f64cf2af-759c-4317-80db-1f352f364669","fa640339-ec64-4e79-9a0c-829fa211c6fa"]
    #for i, story_id in enumerate(stories):
    #    print(f"==============Progress: {i}/{len(stories)} =====================")
    #    print(f"Translating {story_id}")
    #    query = {"id": story_id}
    #    translate_story(query)
    #    print(f"Generating audio for {story_id}")
    #    generate_audio(query)
    #    print(f"Generating audio for words in {story_id}")
    #    generate_audio_for_words_by_translation_json(story_id)