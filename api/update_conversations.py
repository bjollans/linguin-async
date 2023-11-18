from api.update_conversation import update_conversation
import util.db as db

def update_conversations(query):
    conversation_ids = db.list_pending_conversation_ids()
    for conversation_id in conversation_ids:
        update_conversation(conversation_id)