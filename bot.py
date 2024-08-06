#!/home/jason/.pyenv/shims/python3
from bot_instance import bot
import commands.chat_reset_generate  # Import commands modules
import commands.models
import commands.memory
import commands.web
import commands.book
from config import DISCORD_BOT_TOKEN

if __name__ == "__main__":
    bot.run(DISCORD_BOT_TOKEN)

