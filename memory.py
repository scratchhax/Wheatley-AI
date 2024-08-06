from bot_instance import bot
from memory import load_memory, save_memory
import state  # Import the state module

@bot.command(name='set_memory')
async def set_memory(ctx, key: str, *, value: str):
    user_id = str(ctx.author.id)
    memory = load_memory(user_id)
    memory[key] = value
    save_memory(user_id, memory)
    await ctx.send(f"Memory set: **{key}** = {value}")

@bot.command(name='get_memory')
async def get_memory(ctx, key: str = None):
    user_id = str(ctx.author.id)
    memory = load_memory(user_id)
    if key:
        value = memory.get(key, "No memory set for this key.")
        await ctx.send(f"Memory for **{key}**: {value}")
    else:
        if memory:
            memory_list = "\n".join([f"**{k}**: {v}" for k, v in memory.items()])
            await ctx.send(f"All memories:\n{memory_list}")
        else:
            await ctx.send("No memories set.")

@bot.command(name='delete_memory')
async def delete_memory(ctx, key: str = None):
    user_id = str(ctx.author.id)
    memory = load_memory(user_id)
    if key:
        if key in memory:
            del memory[key]
            save_memory(user_id, memory)
            await ctx.send(f"Memory for **{key}** has been deleted.")
        else:
            await ctx.send(f"No memory found for **{key}**.")
    else:
        memory.clear()
        save_memory(user_id, memory)
        await ctx.send("All memories have been deleted.")

