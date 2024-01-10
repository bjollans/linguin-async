from util import gpt
from api.common_responses import success
import util.db as db

def generate_questions(query):
    story_id = query["id"]
    story_content = query["content"]
    question_json = gpt.get_questions_for_story(story_content)
    for question in question_json:
        question["storyId"] = story_id
    db.insert_questions(question_json)
    return success

def generate_questions_for_all_stories():
    stories = db.get_stories_without_question()
    for i, story in enumerate(stories):
        print(f"Generating questions for {story['id']}; {i+1}/{len(stories)}")
        generate_questions({"id": story["id"], "content": story["en"]})
    return success