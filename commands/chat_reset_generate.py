import discord  # Add this import
import os
from bot_instance import bot
import requests
import base64
from memory_utils import load_conversation_history, save_conversation_history, load_memory, get_context_file
from utils import log_debug, split_message, send_long_message, format_json_response, trim_conversation_history
from config import API_BASE_URL, OLLAMA_PARAMETERS
import state  # Import the state module

@bot.command(name='generate')
async def generate(ctx, model: str, *, prompt: str):
    user_id = str(ctx.author.id)
    data = {
        'model': state.conversation_history[user_id].get("default_model", "llama3:latest"),
        'prompt': prompt,
        'options': OLLAMA_PARAMETERS,
        'stream': False
    }
    status_message = await ctx.send("Generating response... Please wait.")
    response = requests.post(f'{API_BASE_URL}/generate', json=data)
    try:
        response_json = response.json()
        formatted_response = format_json_response(response_json)
        await send_long_message(ctx.channel, formatted_response, status_message)
    except json.JSONDecodeError as e:
        log_debug(f"Error: Could not decode JSON response. Raw response: {response.text}")
        await send_long_message(ctx.channel, f"Error: Could not decode JSON response. Raw response: {response.text}", status_message)

@bot.command(name='reset')
async def reset_command(ctx):
    user_id = str(ctx.author.id)
    if user_id in state.conversation_history:
        del state.conversation_history[user_id]
        context_file = get_context_file(user_id)
        if os.path.exists(context_file):
            os.remove(context_file)
    await ctx.send("Conversation history has been reset.")

@bot.command(name='commands')
async def commands_list(ctx):
    help_text = """
    **Bot Commands:**
    - **Chat Commands**: Any message not starting with '!' will be processed as a chat command using the default model.
    - **!reset**: Reset the conversation history.
    - **!generate <model> <prompt>**: Generate a response for the given prompt using the specified model.
    - **!list_models**: List all models available locally.
    - **!show_model <name>**: Show information about the specified model.
    - **!delete_model <name>**: Delete the specified model.
    - **!pull_model <name>**: Pull a model from the model library.
    - **!list_running**: List all running models.
    - **!set_default_model <model>**: Set the default model for chat commands.
    - **!set_memory <key> <value>**: Set a persistent memory value for the user.
    - **!get_memory [<key>]**: Get a persistent memory value for the user. If no key is specified, all memories are returned.
    - **!delete_memory [<key>]**: Delete a persistent memory value for the user. If no key is specified, all memories are deleted.
    - **!summarize_page <url>**: Visit a webpage and summarize its content.
    - **!search <query>**: Search the web using DuckDuckGo and summarize the results.
    - **!read**: Upload an EPUB file and summarize its content.
    - **!ask**: Ask a question about the uploaded book or say summarize all sections for a paragraph book summary.
    """
    for chunk in split_message(help_text):
        await ctx.send(chunk)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Check if the message is a DM or the bot is mentioned
    if isinstance(message.channel, discord.DMChannel) or bot.user.mentioned_in(message):
        # Remove the mention from the message content if mentioned
        if bot.user.mentioned_in(message):
            mention = f"<@{bot.user.id}>"
            if message.content.startswith(mention):
                message.content = message.content.replace(mention, '').strip()

        if message.content.startswith(bot.command_prefix):
            await bot.process_commands(message)
            return

        user_id = str(message.author.id)
        if user_id not in state.conversation_history:
            state.conversation_history[user_id] = load_conversation_history(user_id)

        # Ensure the conversation history is initialized correctly
        if not isinstance(state.conversation_history[user_id], dict):
            state.conversation_history[user_id] = {"history": [], "default_model": "llama3:latest"}

        if "history" not in state.conversation_history[user_id]:
            state.conversation_history[user_id]["history"] = []

        attachments = message.attachments
        if attachments:
            for attachment in attachments:
                if attachment.filename.endswith('.txt'):
                    content = await attachment.read()
                    message.content = content.decode('utf-8')
                elif any(attachment.filename.endswith(ext) for ext in ['.png', '.jpg', '.jpeg']):
                    content = await attachment.read()
                    encoded_image = base64.b64encode(content).decode('utf-8')
                    message.content = f"Image received: {attachment.filename}"

                    data = {
                        'model': 'llava',
                        'prompt': message.content,
                        'images': [encoded_image],
                        'options': OLLAMA_PARAMETERS,
                        'stream': False
                    }

                    status_message = await message.channel.send("Processing image... Please wait.")
                    response = requests.post(f'{API_BASE_URL}/generate', json=data)
                    try:
                        response_json = response.json()
                        filtered_response = {k: v for k, v in response_json.items() if k not in ['context', 'Context']}
                        formatted_response = format_json_response(filtered_response)
                        await send_long_message(message.channel, formatted_response, status_message)
                        return
                    except json.JSONDecodeError as e:
                        log_debug(f"Error: Could not decode JSON response. Raw response: {response.text}")
                        await send_long_message(message.channel, f"Error: Could not decode JSON response. Raw response: {response.text}", status_message)
                        return

        user_memory = load_memory(user_id)
        memory_prompt = "\n".join([f"{key}: {value}" for key, value in user_memory.items()])

        state.conversation_history[user_id]["history"].append({"role": "user", "content": message.content})

        trim_conversation_history(user_id, memory_prompt, state.conversation_history)

        data = {
            'model': state.conversation_history[user_id].get("default_model", "llama3:latest"),
            'messages': [{"role": "system", "content": memory_prompt}] + state.conversation_history[user_id]["history"],
            'options': OLLAMA_PARAMETERS,
            'stream': False
        }

        status_message = await message.channel.send("Processing your message... Please wait.")
        response = requests.post(f'{API_BASE_URL}/chat', json=data)

        try:
            response_json = response.json()
            if 'message' in response_json and response_json['message']['role'] == 'assistant':
                state.conversation_history[user_id]["history"].append(response_json['message'])
                save_conversation_history(user_id, state.conversation_history)
                assistant_message = response_json['message']['content']
                await send_long_message(message.channel, assistant_message, status_message)

        except json.JSONDecodeError as e:
            log_debug(f"Error: Could not decode JSON response. Raw response: {response.text}")
            await send_long_message(message.channel, f"Error: Could not decode JSON response. Raw response: {response.text}", status_message)

