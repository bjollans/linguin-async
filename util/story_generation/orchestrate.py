import random
from util import db
from util.dalle3 import get_img_url_fiction, get_img_url_non_fiction
from util.db import get_stories_by_language, get_stories_in_review, get_story_by_id, get_story_by_title, insert_story_content, get_stories_by_status, set_story_status, update_story
from util.file_utils import download_image_from_url
from util.gpt.gpt import single_chat_completion
from util.gpt.story_generation import evaluate_mini_story, evaluation_min_value, generate_ideas_for_articles, generate_ideas_for_collections, generate_known_fiction_story, generate_mini_story, generate_mini_story_by_committee, generate_mini_story_no_image_jul_2024, generate_mini_story_with_image_jul_2024, generate_non_fiction_story, generate_story_summary, is_story_good
import json

from util.validation.sentence_size import sentences_are_too_long


def generate_one_round_of_content(language, round_size=5):
    print(f"Generating content for {round_size} rounds")
    for i in range(round_size):
        print(f"Generating content for round {i+1}/{round_size}")
        print(f"Generating non-fiction content")
        generate_content_from_collection_name(
            ["History", "Culture", "Geography"], limit=50, language=language, word_count=200)
        generate_content_from_collection_name(
            ["History", "Culture", "Geography"], limit=50, language=language, word_count=300)
        print(f"Generating stories")
        generate_and_save_mini_story_by_committee(language, word_count=200)
        generate_and_save_mini_story_by_committee(language, word_count=200)
        generate_and_save_mini_story_by_committee(language, word_count=300)
        generate_and_save_mini_story_by_committee(language, word_count=300)


def generate_and_save_mini_story(language, word_count=200):
    try:
        story = json.loads(generate_mini_story_with_image_jul_2024(
            language, word_count=word_count))
        if is_story_good(story["story"]):
            print("Generated mini story is good. Inserting.")
            insert_story_content(
                story["title"], story["story"], "Easy", targetLanguage=language, tags="mini story")
        else:
            print("Generated mini story is not good enough. Moving on.")
    except Exception as e:
        print(
            f"Error generating mini story. Moving on. AI Output is not predictable. {e}")
        return


def generate_and_save_mini_story_by_committee(language, word_count=300):
    try:
        story = json.loads(generate_mini_story_by_committee(
            language, word_count=word_count))
        insert_story_content(
            story["title"], story["story"], "Intermediate", targetLanguage=language)
    except Exception as e:
        print(
            f"Error generating mini story. Moving on. AI Output is not predictable. {e}")
        return


def generate_and_save_known_fiction_story(title, language, word_count=300):
    try:
        story_text = generate_known_fiction_story(
            title, language, word_count=word_count)
        insert_story_content(
            title, story_text, "Intermediate", targetLanguage=language)
    except Exception as e:
        print(
            f"Error generating known fiction story. Moving on. AI Output is not predictable. {e}")
        return


def generate_content_from_collection_name(collection_names, limit=10, language="hi", word_count=300):
    print(f"Generating content for {collection_names}")
    try:
        new_story = generate_ideas_for_collections(
            collection_names, limit=limit, language=language, word_count=word_count)
        new_story_json = json.loads(new_story)
        print(f"Inserting content for {collection_names} with title {
              new_story_json['title']}")
        insert_story_content(new_story_json["title"], new_story_json["en"],
                             new_story_json["difficulty"], targetLanguage=language)
    except Exception as e:
        print(f"Error generating content for {
              collection_names}. Moving on. AI Output is not predictable. {e}")
        return


def generate_content(title, idea, is_fiction=False, paragraph_count=3):
    difficulty = "Easy" if paragraph_count < 4 else "Intermediate" if paragraph_count < 6 else "Hard"

    print(f"Generating content for {title}")
    if is_fiction:
        content = generate_known_fiction_story(
            idea, paragraph_count=paragraph_count)
    else:
        content = generate_non_fiction_story(
            idea, paragraph_count=paragraph_count)

    if not sentences_are_too_long(content):
        print(f"Inserting content for {title}")
        insert_story_content(title, content, difficulty)
    else:
        print(f"Skipping content for {title} because sentences are too long")


def generate_images_for_image_pending_stories():
    stories = get_stories_by_status("Image Pending")
    for i, story in enumerate(stories):
        print(f"Generating images for {story['id']}; {i+1}/{len(stories)}")
        generate_images_for_story(story["title"], is_fiction=True)
        set_story_status(story["id"], "Image Review Pending")


def generate_images_for_story(title, is_fiction=False, image_amount=3):
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
        download_image_from_url(
            img_urls[i], f"/Users/bernardjollans/Pictures/Linguin/GeneratedStoryImages/{title}_{i}.png")


def check_story_duplicates(language):
    stories = get_stories_by_language(language)
    prompt = "Which of these stories have the same content? " + str(stories)
    return single_chat_completion(prompt)


def generate_and_save_summaries():
    stories = get_stories_in_review()
    for i, story in enumerate(stories):
        print(f"Generating summary for {story['id']}; {i+1}/{len(stories)}")
        if story["summary"]:
            print("Summary already exists. Skipping.")
            continue
        summary = generate_story_summary(story["en"])
        story["summary"] = summary
        update_story(story)


def generate_and_save_article(lang, tag):
    idea_json = generate_ideas_for_articles(lang, tag)
    content_json = generate_non_fiction_story(idea_json["ideas"][0])
    db.insert_story_content(
        content_json["title"], content_json["article"], "Unknown", lang, tags=tag)
