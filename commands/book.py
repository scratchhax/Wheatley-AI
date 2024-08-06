from bot_instance import bot
import requests
import time
import os
from bs4 import BeautifulSoup
from ebooklib import epub
from memory_utils import load_conversation_history
from utils import log_debug, send_long_message, chunk_text
from config import API_BASE_URL, OLLAMA_PARAMETERS
import state  # Import the state module

def extract_text_from_epub(epub_path):
    book = epub.read_epub(epub_path)
    text = []
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            for paragraph in soup.find_all('p'):
                text.append(paragraph.get_text())
    return '\n'.join(text)

async def summarize_chunk(chunk, model):
    data = {
        'model': model,
        'prompt': f"Summarize the following text in detail:\n\n{chunk}",
        'options': OLLAMA_PARAMETERS,
        'stream': False
    }
    response = requests.post(f'{API_BASE_URL}/generate', json=data)
    response_json = response.json()
    return response_json.get('response', 'No summary available.')

def get_relevant_summaries(question, summaries):
    if "summarize all sections" in question.lower():
        return summaries

    relevant_summaries = []
    keywords = set(question.lower().split())
    for summary in summaries:
        summary_keywords = set(summary.lower().split())
        if keywords & summary_keywords:
            relevant_summaries.append(summary)
        if len(relevant_summaries) >= 5:
            break
    return relevant_summaries

@bot.command(name='read')
async def read(ctx):
    if not ctx.message.attachments:
        await ctx.send("Please attach an EPUB file.")
        return

    attachment = ctx.message.attachments[0]
    if not attachment.filename.endswith('.epub'):
        await ctx.send("Please attach a valid EPUB file.")
        return

    status_message = await ctx.send("Reading and summarizing the book... Please wait.")

    epub_path = f'/tmp/{attachment.filename}'
    await attachment.save(epub_path)

    start_time = time.time()

    try:
        book_text = extract_text_from_epub(epub_path)

        user_id = str(ctx.author.id)
        state.book_contents[user_id] = book_text

        chunks = chunk_text(book_text)
        summaries = []
        for idx, chunk in enumerate(chunks):
            summary = await summarize_chunk(chunk, state.conversation_history[user_id].get("default_model", "llama3:latest"))
            chunk_summary = f"Section {idx + 1} of {len(chunks)}:\n\n{summary}"
            summaries.append(chunk_summary)
            log_debug(f"Processed chunk {idx + 1} of {len(chunks)}: {summary[:100]}...")  # Debug statement
            elapsed_time = int(time.time() - start_time)
            await status_message.edit(content=f"Reading and summarizing the book... Time elapsed: {elapsed_time} seconds. Processed {idx + 1} of {len(chunks)} sections.")

        state.book_summaries[user_id] = summaries

        final_summary = "\n".join(summaries)

        await send_long_message(ctx.channel, final_summary, status_message)
    except Exception as e:
        log_debug(f"Error: {str(e)}")
        await status_message.edit(content=f"Error: Could not read and summarize the book. {str(e)}")
    finally:
        os.remove(epub_path)

@bot.command(name='ask')
async def ask(ctx, *, question: str):
    user_id = str(ctx.author.id)
    if user_id not in state.book_summaries or not state.book_summaries[user_id]:
        await ctx.send("No book content found. Please use the !read command to upload and summarize a book first.")
        return

    status_message = await ctx.send("Processing your question... Please wait.")

    summaries = state.book_summaries[user_id]
    relevant_summaries = get_relevant_summaries(question, summaries)

    if not relevant_summaries:
        await ctx.send("No relevant information found in the book summaries to answer your question.")
        return

    combined_summaries = "\n\n".join(relevant_summaries)
    log_debug(f"Combined summaries: {combined_summaries[:500]}...")  # Debug statement

    try:
        if "summarize all sections" in question.lower():
            prompt = f"Using the following book summaries, create a comprehensive and detailed book report:\n\n{combined_summaries}\n\nDetailed Book Report:"
        else:
            prompt = f"Using the following book summaries, answer the question in detail:\n\n{combined_summaries}\n\nQuestion: {question}"

        data = {
            'model': state.conversation_history[user_id].get("default_model", "llama3:latest"),
            'prompt': prompt,
            'options': OLLAMA_PARAMETERS,
            'stream': False
        }

        response = requests.post(f'{API_BASE_URL}/generate', json=data)
        response_json = response.json()
        answer = response_json.get('response', 'No answer available.')

        log_debug(f"Response length: {len(answer)}")  # Log the length of the response
        log_debug(f"Response content: {answer}")  # Log the content of the response

        await send_long_message(ctx.channel, answer, status_message)
    except Exception as e:
        log_debug(f"Error: {str(e)}")
        await status_message.edit(content=f"Error: Could not get an answer to your question. {str(e)}")

