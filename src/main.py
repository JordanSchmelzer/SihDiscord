import asyncio
import os
import json
import discord  # python3 -m pip install -U discord.py[voice]
from discord.ext import commands, tasks
import dotenv  # pip install -U pyton-dotenv, can read .env files to get secrets (tokens)
import logging

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')


def get_prefix(bot, message):
    """A callable Prefix for our bot. This could be edited to allow per server prefixes."""

    # Notice how you can use spaces in prefixes. Try to keep them simple though.
    prefixes = ['>?', 'lol ', '!?', '!']

    # Check to see if we are outside of a guild. e.g DM's etc.
    if not message.guild:
        # Only allow ? to be used in DMs
        return '?'

    # If we are in a guild, we allow for the user to mention us or use any of the prefixes in our list.
    return commands.when_mentioned_or(*prefixes)(bot, message)


# set intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# the bot
bot = commands.Bot(command_prefix=get_prefix, intents=intents)

# get token
dotenv.load_dotenv()

# store token credentials in .env (make it a secret) - gitignore!!!
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')


@bot.event
async def on_ready():
    """http://discordpy.readthedocs.io/en/rewrite/api.html#discord.on_ready"""

    print(f'\n\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\n')


async def load_extensions():
    # Below cogs represents our folder our cogs are in. Following is the file name. So 'meme.py' in cogs,
    # would be cogs.meme Think of it like a dot path import
    initial_extensions = ['cogs.cmds',
                          'cogs.events',
                          'cogs.music']

    # Here we load our extensions(cogs) listed above in [initial_extensions].
    if __name__ == '__main__':
        for extension in initial_extensions:
            await bot.load_extension(extension)


async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)


asyncio.run(main())
