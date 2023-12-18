# bot.py
# import required dependencies
import os
import discord  # python3 -m pip install -U discord.py[voice]
from discord.ext import commands
from discord import FFmpegPCMAudio
import youtube_dl
from dotenv import load_dotenv  # pip install -U pyton-dotenv, can read .env files to get secrets (tokens)
import json

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# object that represents a connection to discord
client = commands.Bot(command_prefix='!', intents=intents)

# store token credentials in .env (make it a secret) - gitignore!!!
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')


@client.event
# implement on_ready event handler, handles the event when client has established connection and is done prepping data
# on_ready is a good time to run setup related code. event immediately after boot-- the app has access to things here.
async def on_ready():
    print(f'{client.user} connected to discord. ready for further action')

    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(f'{guild.name}(id: {guild.id})')

    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')


@client.command()
async def join(ctx):
    channel = ctx.author.voice.channel
    await ctx.channel.connect()


@client.command()
async def leave(ctx):
    await ctx.voice_client.disconnect()


@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hello {member.name}, welcome to my DEV environment!'
    )


@client.command()
async def respond(ctx):
    print("i saw a message")
    await ctx.channel.send("response")


@client.command()
async def play(ctx, url: str):
    channel = ctx.message.author.voice.channel
    print(channel)
    user = ctx.message.author
    print(user)
    vc = user.voice.channel
    print(vc)

    audio_source = 'heading-south.mp3'
    voice_client = discord.utils.get(client.voice_clients, guild=ctx.guild)
    print(voice_client)

    if voice_client:
        await ctx.send('Saw !play, but already connected to another voice channel')
        return

    voice_channel = ctx.author.voice.channel
    voice_client = await voice_channel.connect()

    voice_client.play(discord.FFmpegPCMAudio(audio_source))


"""
    # download the youtube video
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            os.rename(file, "song.mp3")

"""

# this has to be at the end, or it won't see any of the commands
client.run(TOKEN)