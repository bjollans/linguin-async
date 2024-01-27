from supabase import create_client, Client
import os
from dotenv import load_dotenv
load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)


def upload_audio_to_bucket(filepath, path_on_bucket, bucket="storySound"):
    with open(filepath, 'rb') as f:
        supabase.storage.from_(bucket).upload(
            file=f, path=path_on_bucket, file_options={"content-type": "audio/mpeg"})
    return f"{url}/storage/v1/object/public/{bucket}/{path_on_bucket}"


def file_exists(path_on_bucket, bucket):
    try:
        supabase.storage.from_(bucket).download(path_on_bucket)
        return True
    except:
        return False


def update_story(story):
    response = supabase \
        .table('stories') \
        .update(story) \
        .eq("id", story["id"]) \
        .execute()
    return response.data


def get_story_by_id(story_id):
    response = supabase \
        .table('stories') \
        .select("*") \
        .eq("id", story_id) \
        .single() \
        .execute()
    return response.data


def get_story_by_title(title):
    response = supabase \
        .table('stories') \
        .select("*") \
        .eq("title", title) \
        .single() \
        .execute()
    return response.data


def get_stories_without_content():
    response = supabase \
        .table('stories') \
        .select("id") \
        .is_("content", "null") \
        .execute()
    return response.data


def get_stories_done_without_content():
    response = supabase \
        .table('stories') \
        .select("id") \
        .is_("content", "null") \
        .eq("status", "Done") \
        .execute()
    return response.data


def get_stories_without_question():
    all_stories = get_all_stories_with_content()
    story_ids_with_questions = _get_story_ids_with_questions()
    stories_without_questions = [
        story for story in all_stories if story["id"] not in story_ids_with_questions]
    return stories_without_questions


def get_all_stories():
    response = supabase \
        .table('stories') \
        .select("*") \
        .execute()
    return response.data

def get_all_stories_with_content():
    response = supabase \
        .table('stories') \
        .select("*") \
        .not_.is_("content", "null") \
        .execute()
    return response.data


def _get_story_ids_with_questions():
    response = supabase.table('storyQuestions') \
        .select('storyId') \
        .execute()
    return list(set([x["storyId"] for x in response.data]))


def _get_story_ids_read_by_user(user_id):
    response = supabase \
        .table('userStoriesRead') \
        .select("storyId") \
        .eq("userId", user_id) \
        .execute()
    return list(set([x["storyId"] for x in response.data]))


def get_stories_read_by_user(user_id):
    story_ids = _get_story_ids_read_by_user(user_id)
    stories = []
    for story_id in story_ids:
        stories.append(get_story_by_id(story_id))
    return stories


def get_users_who_have_read_any_story():
    response = supabase \
        .table('userStoriesRead') \
        .select("userId") \
        .execute()
    return list(set([x["userId"] for x in response.data]))


def upsert_user_read_statistics(user_id, word_list):
    response = supabase \
        .table('userReadStatistics') \
        .upsert({"userId": user_id, "wordsSeen": word_list}) \
        .execute()
    return response.data


def insert_questions(questions):
    response = supabase \
        .table('storyQuestions') \
        .insert(questions) \
        .execute()
    return response.data


def get_stories_without_audio():
    response = supabase \
        .table('stories') \
        .select("id") \
        .is_("audioUrl", "null") \
        .not_.is_("content", "null") \
        .execute()
    return response.data


def get_messages_by_conversation_id(conversation_id):
    response = supabase \
        .table('messages') \
        .select("role, content") \
        .eq("conversationId", conversation_id) \
        .order("createdAt") \
        .execute()
    return response.data


def get_conversation_by_id(conversation_id):
    response = supabase \
        .table('conversations') \
        .select("*") \
        .eq("id", conversation_id) \
        .single() \
        .execute()
    return response.data


def set_conversation_done(conversation_id):
    response = supabase \
        .table('conversations') \
        .update({"status": "done"}) \
        .eq("id", conversation_id) \
        .execute()
    return response.data


def insert_message(message):
    # TODO: Make sure the message count has not changed, to avoid race conditions
    response = supabase \
        .table('messages') \
        .insert(message) \
        .execute()
    return response.data


def list_pending_conversation_ids():
    response = supabase \
        .table('conversations') \
        .select("id") \
        .eq("status", "pending") \
        .execute()
    return response.data


def insert_story_content(title, content, difficulty, targetLanguage="hi"):
    response = supabase \
        .table('stories') \
        .insert({"title": title,
                 "en": content,
                 "difficulty": difficulty,
                 "translationLanguage": "en",
                 "targetLanguage": targetLanguage,
                 "status": "Content Review Pending"}) \
        .execute()
    return response.data


if __name__ == "__main__":
    print(get_stories_without_audio())
