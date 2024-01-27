import random
from util.dalle3 import get_img_url_fiction, get_img_url_non_fiction
from util.db import get_story_by_id, get_story_by_title, insert_story_content
from util.file_utils import download_image_from_url
from util.gpt import generate_known_fiction_story, generate_non_fiction_story, react_to_image


def generate_content(title, idea, is_fiction=False, paragraph_count = 3):
    difficulty = "Easy" if paragraph_count < 4 else "Intermediate" if paragraph_count < 6 else "Hard"

    print(f"Generating content for {title}")
    if is_fiction:
        content = generate_known_fiction_story(idea, paragraph_count=paragraph_count)
    else:
        content = generate_non_fiction_story(idea, paragraph_count=paragraph_count)

    print(f"Inserting content for {title}")
    insert_story_content(title, content, difficulty)


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