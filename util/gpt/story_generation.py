
import random
from util.db import get_texts_stories_in_collection
from util.gpt.gpt import chain_of_thought, react_to_image, single_chat_completion


def generate_mini_story():
    img_url = f'https://mini-story-images.s3.eu-west-1.amazonaws.com/{random.randint(0,80)}.jpeg'
    prompt = 'Write me a short story (and title) based on this picture in json format as `{"title":"...","story":"..."}`. Just return the plain JSON without formatting or backticks. The story should be for an A1 English learner. It should be around 2 paragraphs long. It should be set in India, but do not mention "India" or elude to it in the story. Write the story using the Heros Journey structure. Start with the hero in a normal setting, introduce a challenge that leads them on an adventure. Have them face obstacles, receive help from a mentor, and overcome a major crisis. Conclude with the hero returning transformed, bringing back something valuable to their original home. Do not use words like "Hero" or "Quest". The setting should be general day to day and not epic.'
    return react_to_image(prompt, img_url)

def generate_ideas_for_collections(collectionNames, limit=10):
    stories_json = []
    for collectionName in collectionNames:
        stories_json += get_texts_stories_in_collection(collectionName, limit=limit)
    random.shuffle(stories_json)
    stories_json = stories_json[:limit]
    prompt = f'Give me another row for this json. Just give me the new row as plain json without formatting: {stories_json}'
    return single_chat_completion(prompt)


def generate_non_fiction_story(topic, paragraph_count=3):
    return chain_of_thought([
        f"What do you know about {topic}. Give me {paragraph_count} paragraphs:",
        "Simplify the language and use more common words.",
        "Put every sentence in a new line.",
    ])


def generate_known_fiction_story(title, paragraph_count=3):
    return chain_of_thought([
        f'Tell me the story "{title}" in {paragraph_count} paragraphs:',
        "Simplify the language and use more common words.",
        "Put every sentence in a new line.",
    ])