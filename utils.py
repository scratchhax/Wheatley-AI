import json
import os
import requests
from bs4 import BeautifulSoup

from config import DEBUG, MAX_LENGTH, CHUNK_SIZE

def log_debug(message):
    if DEBUG:
        print(message)

def split_message(message, max_length=2000):
    return [message[i:i + max_length] for i in range(0, len(message), max_length)]

def get_context_file(user_id):
    return f'/tmp/conversation_history_{user_id}.json'

def get_memory_file(user_id):
    return f'/tmp/memory_{user_id}.json'

def format_json_response(response_json):
    filtered_response = {k: v for k, v in response_json.items() if k not in ['context', 'Context']}
    formatted_response = []
    for key, value in filtered_response.items():
        if isinstance(value, dict):
            formatted_response.append(f"**{key.capitalize()}**:")
            for sub_key, sub_value in value.items():
                formatted_response.append(f"  - **{sub_key.capitalize()}**: {sub_value}")
        elif isinstance(value, list):
            formatted_response.append(f"**{key.capitalize()}**:")
            if all(isinstance(item, dict) for item in value):
                for idx, item in enumerate(value, start=1):
                    formatted_response.append(f"  - **Item {idx}:**")
                    for sub_key, sub_value in item.items():
                        formatted_response.append(f"    - **{sub_key.capitalize()}**: {sub_value}")
            else:
                for item in value:
                    formatted_response.append(f"  - {item}")
        else:
            formatted_response.append(f"**{key.capitalize()}**: {value}")
    return "\n".join(formatted_response)

def trim_conversation_history(user_id, memory_prompt, conversation_history):
    conversation = conversation_history[user_id]["history"]
    combined_length = len(memory_prompt) + sum(len(json.dumps(msg)) for msg in conversation)

    while combined_length > MAX_LENGTH and len(conversation) > 1:
        removed_msg = conversation.pop(0)
        combined_length -= len(json.dumps(removed_msg))

def chunk_text(text, chunk_size=CHUNK_SIZE):
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

async def send_long_message(channel, content, status_message=None):
    message_chunks = split_message(content)
    if status_message:
        await status_message.edit(content=message_chunks[0])
        for chunk in message_chunks[1:]:
            await channel.send(chunk)
    else:
        for chunk in message_chunks:
            await channel.send(chunk)



def search_duckduckgo(query):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    url = f'https://html.duckduckgo.com/html/?q={query}'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return parse_duckduckgo_results(response.text)

def parse_duckduckgo_results(html):
    soup = BeautifulSoup(html, 'html.parser')
    results = []
    for result in soup.find_all('a', class_='result__a'):
        results.append(result.get_text())
    return results

