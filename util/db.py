import os
from supabase import create_client, Client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)


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
