import discord  # Add this import
import requests
from bot_instance import bot
from bs4 import BeautifulSoup  # Add this import
import json  # Add this import
from utils import log_debug, send_long_message, search_duckduckgo
from config import API_BASE_URL, OLLAMA_PARAMETERS
import state  # Import the state module

@bot.command(name='summarize_page')
async def summarize_page(ctx, url: str):
    user_id = str(ctx.author.id)
    status_message = await ctx.send("Visiting page and summarizing... Please wait.")
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        text_content = " ".join(p.get_text() for p in soup.find_all('p'))

        data = {
            'model': state.conversation_history[user_id].get("default_model", "llama3:latest"),
            'prompt': f"Summarize the following content:\n\n{text_content}",
            'options': OLLAMA_PARAMETERS,
            'stream': False
        }

        llm_response = requests.post(f'{API_BASE_URL}/generate', json=data)
        response_json = llm_response.json()

        summary = response_json.get('response', 'No summary available.')

        await send_long_message(ctx.channel, summary, status_message)
    except requests.RequestException as e:
        await status_message.edit(content=f"Error: Could not retrieve the page. {str(e)}")
    except json.JSONDecodeError as e:
        log_debug(f"Error: Could not decode JSON response. Raw response: {llm_response.text}")
        await send_long_message(ctx.channel, f"Error: Could not decode JSON response. Raw response: {llm_response.text}", status_message)
    except discord.HTTPException as e:
        log_debug(f"Error: Discord HTTP exception. {str(e)}")
        await ctx.send(f"Error: Discord HTTP exception. {str(e)}")
    except Exception as e:
        log_debug(f"Unexpected error: {str(e)}")
        await ctx.send(f"Unexpected error: {str(e)}")

@bot.command(name='search')
async def search(ctx, *, query: str):
    user_id = str(ctx.author.id)
    status_message = await ctx.send("Searching... Please wait.")
    try:
        duckduckgo_results = search_duckduckgo(query)

        if not duckduckgo_results:
            await status_message.edit(content="No search results found.")
            return

        combined_text = "\n".join(duckduckgo_results)

        data = {
            'model': state.conversation_history[user_id].get("default_model", "llama3:latest"),
            'prompt': f"Summarize the following search results:\n\n{combined_text}",
            'options': OLLAMA_PARAMETERS,
            'stream': False
        }

        response = requests.post(f'{API_BASE_URL}/generate', json=data)
        response_json = response.json()
        summary = response_json.get('response', 'No summary available.')

        await send_long_message(ctx.channel, summary, status_message)
    except requests.RequestException as e:
        await status_message.edit(content=f"Error: Could not complete search. {str(e)}")
    except json.JSONDecodeError as e:
        log_debug(f"Error: Could not decode JSON response. Raw response: {response.text}")
        await send_long_message(ctx.channel, f"Error: Could not decode JSON response. Raw response: {response.text}", status_message)
    except discord.HTTPException as e:
        log_debug(f"Error: Discord HTTP exception. {str(e)}")
        await ctx.send(f"Error: Discord HTTP exception. {str(e)}")
    except Exception as e:
        log_debug(f"Unexpected error: {str(e)}")
        await ctx.send(f"Unexpected error: {str(e)}")

