# main.py
# import required dependencies
import os
import discord  # python3 -m pip install -U discord.py[voice]
from discord.ext import commands
from dotenv import load_dotenv  # pip install -U pyton-dotenv, can read .env files to get secrets (tokens)
import asyncio

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# object that represents a connection to discord
bot = commands.Bot(command_prefix='!', intents=intents)

# store token credentials in .env (make it a secret) - gitignore!!!
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')


async def load():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')
            print(f'cogs.{filename[:-3]}')


async def main():
    await load()
    await bot.start(TOKEN)


asyncio.run(main())
