# bot.py
import os
import discord

intents = discord.Intents.default()
intents.message_content = True

# object that represents a connection to discord
client = discord.Client(intents=intents)

# pip install -U python-dotenv
# can read from .env files to get secret variables
from dotenv import load_dotenv

load_dotenv()

# store token credentials in .env (make it a secret)
# print(DISCORD_TOKEN)
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
# print('the token is:' + TOKEN)

@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to my DEV!'
    )

@client.event
async def on_message(message):
    print("i saw a message")
    print(message.content)
    # below prevents recursive calls if the bot were to answer itself
    if message.author == client.user:
        return

    if message.content == '!respond':
        response = 'hello'
        await message.channel.send(response)
        print('hey I printed something')

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

# launches the client using the bots token
client.run(TOKEN)