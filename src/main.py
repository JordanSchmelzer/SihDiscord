import asyncio
import os
import discord  # python3 -m pip install -U discord.py[voice]
from discord.ext import commands
import dotenv  # pip install -U pyton-dotenv, can read .env files to get Secrets (tokens)
import logging
import json


# import youtube_dl pip install git+https://github.com/ytdl-org/youtube-dl.git@master#egg=youtube_dl
# you have to use this one or it wont work. i think the germans took it down


def get_prefix(bot, message):
    """A callable Prefix for our bot. This could be edited to allow per server prefixes."""

    # Notice how you can use spaces in prefixes. Try to keep them simple though.
    prefixes = ["$", "?", ".", "!"]

    # Check to see if we are outside of a guild. e.g DM's etc.
    if not message.guild:
        # Only allow ! to be used in DMs
        return "!"

    # If we are in a guild, we allow for the user to mention us or use any of the prefixes in our list.
    return commands.when_mentioned_or(*prefixes)(bot, message)


# set intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# the bot
bot = commands.Bot(command_prefix=get_prefix, intents=intents)

# custom logging
handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")


# copy paste from https://github.com/Darkempire78/Music-Discord-Bot/blob/main/emojis.json
class CreateEmojiList:
    def __init__(self, emojiList):
        self.youtubeLogo = emojiList["YoutubeLogo"]
        self.true = emojiList["True"]
        self.false = emojiList["False"]
        self.alert = emojiList["Alert"]


with open("src/Emojis/emojis.json", "r") as emojiList:
    emojiList = json.load(emojiList)
    emojiList = {
        "YoutubeLogo": emojiList["YouTubeLogo"],
        "True": emojiList["True"],
        "False": emojiList["False"],
        "Alert": emojiList["Alert"],
    }

# Emojis
bot.emojiList = CreateEmojiList(emojiList)

# get token
dotenv.load_dotenv("./src/Secrets/.env")

# store token credentials in .env (make it a secret) - gitignore!!!
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("DISCORD_GUILD")


@bot.event
async def on_ready():
    """http://discordpy.readthedocs.io/en/rewrite/api.html#discord.on_ready"""

    print(
        f"\n\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\n"
    )


async def load_extensions():
    # Below Cogs represents our folder our Cogs are in. Following is the file name. So 'meme.py' in Cogs,
    # would be Cogs.meme Think of it like a dot path import
    initial_extensions = [
        "Cogs.cmds",
        "Cogs.events",
        "Cogs.music",
        "Cogs.help",
    ]
    # Here we load our extensions(Cogs) listed above in [initial_extensions].
    if __name__ == "__main__":
        for extension in initial_extensions:
            await bot.load_extension(extension)


async def clear_songs():
    for file in os.listdir("./src/Songs"):
        if file.endswith(".mp3"):
            os.remove("./src/Songs/" + file)


async def main():
    async with bot:
        await load_extensions()
        # await clear_songs()
        await bot.start(TOKEN)
        bot.run(
            token=TOKEN,
            reconnect=True,
            log_handler=handler,
        )


asyncio.run(main())
