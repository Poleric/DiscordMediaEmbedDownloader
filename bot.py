import os

import discord
from discord.ext import commands
import logging
import sys

from extractor import save_media, NotValidQuery
from extractor.exceptions import ScrapingException, MediaNotFound


BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not BOT_TOKEN:
    logging.exception("DISCORD_BOT_TOKEN is required. Set the bot token as an environment variable with the key DISCORD_BOT_TOKEN")
    sys.exit()

discord.utils.setup_logging()
bot = commands.Bot(
    command_prefix=".",
    activity=discord.CustomActivity("Watching~"),
    intents=discord.Intents.all(),

    description="Downloads any media embed in a message locally."
)


@bot.listen()
async def on_message(msg: discord.Message):
    if msg.embeds:
        ctx = await bot.get_context(msg)
        await ctx.invoke(save, msg=msg)


@bot.command()
async def save(ctx, msg: discord.Message):
    clean_content = msg.content.strip("<>|\"")

    try:
        save_media(clean_content)
    except NotValidQuery:
        logging.exception(f"Saving {clean_content} is not supported yet.")
        await msg.add_reaction("❓")
    except MediaNotFound:
        logging.exception(f"Media is not found {clean_content}.")
        await msg.add_reaction("❌")
    except ScrapingException:
        logging.exception(f"Error encountered when saving {clean_content}")
        await msg.add_reaction("❌")
    else:  # no errors
        await msg.add_reaction("✅")


async def main():
    await bot.start(BOT_TOKEN)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
