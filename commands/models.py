from bot_instance import bot
import requests
from memory_utils import load_conversation_history, save_conversation_history
from utils import log_debug, format_json_response, send_long_message
from config import API_BASE_URL
import state  # Import the state module

@bot.command(name='list_models')
async def list_models(ctx):
    status_message = await ctx.send("Listing models... Please wait.")
    response = requests.get(f'{API_BASE_URL}/tags')
    try:
        response_json = response.json()
        formatted_response = format_json_response(response_json)
        await send_long_message(ctx.channel, formatted_response, status_message)
    except json.JSONDecodeError as e:
        log_debug(f"Error: Could not decode JSON response. Raw response: {response.text}")
        await send_long_message(ctx.channel, f"Error: Could not decode JSON response. Raw response: {response.text}", status_message)

@bot.command(name='show_model')
async def show_model(ctx, name: str):
    data = {'name': name, 'stream': False}
    status_message = await ctx.send("Showing model information... Please wait.")
    response = requests.post(f'{API_BASE_URL}/show', json=data)
    try:
        response_json = response.json()
        formatted_response = format_json_response(response_json)
        await send_long_message(ctx.channel, formatted_response, status_message)
    except json.JSONDecodeError as e:
        log_debug(f"Error: Could not decode JSON response. Raw response: {response.text}")
        await send_long_message(ctx.channel, f"Error: Could not decode JSON response. Raw response: {response.text}", status_message)

@bot.command(name='delete_model')
async def delete_model(ctx, name: str):
    data = {'name': name, 'stream': False}
    status_message = await ctx.send("Deleting model... Please wait.")
    response = requests.delete(f'{API_BASE_URL}/delete', json=data)
    try:
        response_json = response.json()
        formatted_response = format_json_response(response_json)
        await send_long_message(ctx.channel, formatted_response, status_message)
    except json.JSONDecodeError as e:
        log_debug(f"Error: Could not decode JSON response. Raw response: {response.text}")
        await send_long_message(ctx.channel, f"Error: Could not decode JSON response. Raw response: {response.text}", status_message)

@bot.command(name='pull_model')
async def pull_model(ctx, name: str):
    data = {'name': name, 'stream': False}
    status_message = await ctx.send("Pulling model... Please wait.")
    response = requests.post(f'{API_BASE_URL}/pull', json=data)
    try:
        response_json = response.json()
        formatted_response = format_json_response(response_json)
        await send_long_message(ctx.channel, formatted_response, status_message)
    except json.JSONDecodeError as e:
        log_debug(f"Error: Could not decode JSON response. Raw response: {response.text}")
        await send_long_message(ctx.channel, f"Error: Could not decode JSON response. Raw response: {response.text}", status_message)

@bot.command(name='list_running')
async def list_running(ctx):
    status_message = await ctx.send("Listing running models... Please wait.")
    response = requests.get(f'{API_BASE_URL}/ps')
    try:
        response_json = response.json()
        formatted_response = format_json_response(response_json)
        await send_long_message(ctx.channel, formatted_response, status_message)
    except json.JSONDecodeError as e:
        log_debug(f"Error: Could not decode JSON response. Raw response: {response.text}")
        await send_long_message(ctx.channel, f"Error: Could not decode JSON response. Raw response: {response.text}", status_message)

@bot.command(name='set_default_model')
async def set_default_model(ctx, model: str):
    user_id = str(ctx.author.id)
    if user_id not in state.conversation_history:
        state.conversation_history[user_id] = load_conversation_history(user_id)
    state.conversation_history[user_id]["default_model"] = model
    save_conversation_history(user_id, state.conversation_history)
    await ctx.send(f"Default model set to {model}")

