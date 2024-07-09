from supabase import create_client, Client
import os
from dotenv import load_dotenv
load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)


def upload_audio_to_bucket(filepath, path_on_bucket, bucket="storySound"):
    with open(filepath, 'rb') as f:
        # update if file already exists else upload
        if file_exists(path_on_bucket, bucket):
            supabase.storage.from_(bucket).update(
                file=f, path=path_on_bucket, file_options={"content-type": "audio/mpeg"})
        else:
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


def update_story_translation(story_translation):
    response = supabase \
        .table('storyTranslations') \
        .update(story_translation) \
        .eq("id", story_translation["id"]) \
        .execute()
    return response.data[0]["id"]


def insert_story_translation(story_translation):
    response = supabase \
        .table('storyTranslations') \
        .insert(story_translation) \
        .execute()
    return response.data[0]["id"]


def mark_other_story_translations_for_story_as_not_visible(story_translation_id, story_id):
    response = supabase \
        .table('storyTranslations') \
        .update({"visible": False}) \
        .eq("storyId", story_id) \
        .neq("id", story_translation_id) \
        .execute()
    return response.data


def mark_story_translation_as_visible(story_translation_id):
    response = supabase \
        .table('storyTranslations') \
        .update({"visible": True}) \
        .eq("id", story_translation_id) \
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


def get_stories_by_ids(story_ids, columns='*', limit=10):
    response = supabase \
        .table('stories') \
        .select(columns) \
        .in_("id", story_ids) \
        .limit(limit) \
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


def get_stories_by_status(status):
    response = supabase \
        .table('stories') \
        .select("*") \
        .eq("status", status) \
        .execute()
    return response.data


def get_stories_in_review():
    response = supabase \
        .table('stories') \
        .select("*") \
        .neq("status", "Done") \
        .execute()
    return response.data


def set_story_status(story_id, status):
    response = supabase \
        .table('stories') \
        .update({"status": status}) \
        .eq("id", story_id) \
        .execute()
    return response.data


def get_stories_without_content():
    response = supabase \
        .table('stories') \
        .select("id") \
        .is_("content", "null") \
        .execute()
    return response.data


def get_story_ids_done_without_translation():
    response_translation = supabase \
        .table('storyTranslations') \
        .select("storyId") \
        .execute()
    story_ids_with_translation = list(
        set([x["storyId"] for x in response_translation.data]))

    response_stories = supabase \
        .table('stories') \
        .select("id") \
        .eq("status", "Done") \
        .execute()
    all_ids = list(set([x["id"] for x in response_stories.data]))

    stories_without_translation = [
        story for story in all_ids if story not in story_ids_with_translation]
    return stories_without_translation


def get_story_tranlation_idsby_language(language):
    response = supabase \
        .table('storyTranslations') \
        .select("id") \
        .eq("targetLanguage", language) \
        .execute()
    return response.data


def get_stories_done_without_images():
    response = supabase \
        .table('stories') \
        .select("id") \
        .is_("imageUrl", "null") \
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


def get_all_visible_story_translations():
    response = supabase \
        .table('storyTranslations') \
        .select("*") \
        .eq('visible', True) \
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


def get_story_translations_without_audio(target_language=None):
    response = supabase \
        .table('storyTranslations') \
        .select("*") \
        .is_("audioUrl", "null") \
        .not_.is_("content", "null")
    if target_language:
        response = response.eq("targetLanguage", target_language)
    response = response.execute()
    return response.data


def get_story_translation_by_id(story_translation_id):
    response = supabase \
        .table('storyTranslations') \
        .select("*") \
        .eq("id", story_translation_id) \
        .single() \
        .execute()
    return response.data


def get_story_translation_by_story_id_and_lang(story_id, target_language):
    response = supabase \
        .table('storyTranslations') \
        .select("*") \
        .eq("storyId", story_id) \
        .eq("targetLanguage", target_language) \
        .single() \
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


def insert_story_content(title, content, difficulty, targetLanguage="hi", tags=""):
    response = supabase \
        .table('stories') \
        .insert({"title": title,
                 "en": content,
                 "difficulty": difficulty,
                 "targetLanguage": targetLanguage,
                 "status": "Content Review Pending",
                 "tags": tags}) \
        .execute()
    return response.data


def get_stories_by_language(language):
    response = supabase \
        .table('stories') \
        .select("title, en") \
        .eq("targetLanguage", language) \
        .execute()
    return response.data


def get_collection_names_for_story_id(storyId):
    response = supabase \
        .table('storiesToCollections') \
        .select("collectionName") \
        .eq("storyId", storyId) \
        .execute()
    return response.data


def get_story_ids_for_collection_name(collectionName):
    response = supabase \
        .table('storiesToCollections') \
        .select("storyId") \
        .eq("collectionName", collectionName) \
        .execute()
    return response.data


def get_story_titles_for_language(language):
    response = supabase \
        .table('stories') \
        .select("title") \
        .eq("targetLanguage", language) \
        .execute()
    return response.data


def get_article_titles_for_language(language, tag):
    response = supabase \
        .table('stories') \
        .select("title") \
        .eq("targetLanguage", language) \
        .like("tags", f'%{tag}%') \
        .execute()
    return response.data


def get_texts_stories_in_collection(collectionName, limit=10):
    storyIds = [obj["storyId"]
                for obj in get_story_ids_for_collection_name(collectionName)]
    stories = get_stories_by_ids(
        storyIds, columns="title, en, difficulty", limit=limit)
    return stories


if __name__ == "__main__":
    print(get_stories_without_audio())
