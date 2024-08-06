import json
import os

def get_context_file(user_id):
    return f'/tmp/conversation_history_{user_id}.json'

def get_memory_file(user_id):
    return f'/tmp/memory_{user_id}.json'

def load_conversation_history(user_id):
    context_file = get_context_file(user_id)
    if os.path.exists(context_file):
        with open(context_file, 'r') as file:
            return json.load(file)
    return {"history": [], "default_model": "llama3:latest"}

def save_conversation_history(user_id, conversation_history):
    context_file = get_context_file(user_id)
    with open(context_file, 'w') as file:
        json.dump(conversation_history, file, indent=2)

def load_memory(user_id):
    memory_file = get_memory_file(user_id)
    if os.path.exists(memory_file):
        with open(memory_file, 'r') as file:
            return json.load(file)
    return {}

def save_memory(user_id, memory_data):
    memory_file = get_memory_file(user_id)
    with open(memory_file, 'w') as file:
        json.dump(memory_data, file, indent=2)

