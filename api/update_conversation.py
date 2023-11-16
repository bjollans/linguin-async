import json
import util.db as db
import util.gpt as gpt
from api.common_responses import success

def _get_system_prompt(conversation_id):
    conversation = db.get_conversation_by_id(conversation_id)
    return conversation["systemPrompt"]

def update_conversation(query):
    conversation_id = query["id"]
    messages = db.get_messages_by_conversation_id(conversation_id)
    answer = gpt.get_next_message(messages, _get_system_prompt(conversation_id))
    answer["conversationId"] = conversation_id
    db.insert_message(answer)
    return success