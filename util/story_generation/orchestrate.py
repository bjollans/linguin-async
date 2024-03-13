import random
from util.dalle3 import get_img_url_fiction, get_img_url_non_fiction
from util.db import get_story_by_id, get_story_by_title, insert_story_content, get_stories_by_status, set_story_status
from util.file_utils import download_image_from_url
from util.gpt.story_generation import generate_ideas_for_collections, generate_known_fiction_story, generate_mini_story, generate_non_fiction_story
import json


def generate_one_round_of_content(round_size=5):
    print(f"Generating content for {round_size} rounds")
    for i in range(round_size):
        print(f"Generating content for round {i+1}/{round_size}")
        print(f"Generating non-fiction content")
        generate_content_from_collection_name(["History", "Culture", "Geography"], limit=50)
        print(f"Generating fiction content")
        generate_content_from_collection_name(["Stories"])
        print(f"Generating mini story")
        generate_and_save_mini_story()


def generate_and_save_mini_story():
    try:
        story = json.loads(generate_mini_story())
        insert_story_content(story["title"], story["en"], "Easy")
    except:
        print(f"Error generating mini story. Moving on. AI Output is not predictable.")
        return


def generate_content_from_collection_name(collection_names, limit=10):
    print(f"Generating content for {collection_names}")
    try:
        new_story=generate_ideas_for_collections(collection_names, limit=limit)
        new_story_json = json.loads(new_story)
        insert_story_content(new_story_json["title"], new_story_json["en"], new_story_json["difficulty"])
    except:
        print(f"Error generating content for {collection_names}. Moving on. AI Output is not predictable.")
        return


def generate_content(title, idea, is_fiction=False, paragraph_count = 3):
    difficulty = "Easy" if paragraph_count < 4 else "Intermediate" if paragraph_count < 6 else "Hard"

    print(f"Generating content for {title}")
    if is_fiction:
        content = generate_known_fiction_story(idea, paragraph_count=paragraph_count)
    else:
        content = generate_non_fiction_story(idea, paragraph_count=paragraph_count)

    print(f"Inserting content for {title}")
    insert_story_content(title, content, difficulty)


def generate_images_for_image_pending_stories():
    stories = get_stories_by_status("Image Pending")
    for i, story in enumerate(stories):
        print(f"Generating images for {story['id']}; {i+1}/{len(stories)}")
        generate_images_for_story(story["title"], is_fiction=True)
        set_story_status(story["id"], "Image Review Pending")


def generate_images_for_story(title, is_fiction=False, image_amount = 3):
    print(f"Generating images for {title}")
    try:
        story = get_story_by_title(title)
    except:
        print(f"Story {title} not found")
        return
    content = story["en"]
    img_urls = []
    if is_fiction:
        for i in range(image_amount):
            print(f"Generating image {i} for {title}")
            img_urls.append(get_img_url_fiction(content))
            print(f"image url: {img_urls[i]}")
    else:
        for i in range(image_amount):
            print(f"Generating image {i} for {title}")
            img_urls.append(get_img_url_non_fiction(content))
            print(f"image url: {img_urls[i]}")
    for i in range(image_amount):
        print(f"Downloading image {i} for {title}")
        download_image_from_url(img_urls[i], f"/Users/bernardjollans/Pictures/Linguin/GeneratedStoryImages/{title}_{i}.png")