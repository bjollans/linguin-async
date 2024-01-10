import os
from dotenv import load_dotenv
load_dotenv()
from supabase import create_client, Client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

def upload_audio_to_bucket(filepath, path_on_bucket, bucket="storySound"):
    with open(filepath, 'rb') as f:
        supabase.storage.from_(bucket).upload(file=f,path=path_on_bucket, file_options={"content-type": "audio/mpeg"})
    return f"{url}/storage/v1/object/public/{bucket}/{path_on_bucket}"

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

def get_stories_without_content():
    response = supabase \
        .table('stories') \
        .select("id") \
        .is_("content", "null") \
        .execute()
    return response.data

def get_stories_without_audio():
    response = supabase \
        .table('stories') \
        .select("id") \
        .is_("audioUrl", "null") \
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
    #TODO: Make sure the message count has not changed, to avoid race conditions
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


if __name__ == "__main__":
    print(get_stories_without_audio())