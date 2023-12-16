# discord.py

import os

from dotenv import load_dotenv

load_dotenv()
#store token credentials in .env (make it a secret)
TOKEN = os.getenv('DISCORD_TOKEN')

#object that represents a connection to discord
client = discord.Cllient()

@client.event
#impliment on_ready event handler, handles the event when client has established connection and is done prepping data
async def on_ready():
    print(f'{client.user} connected to discrod. ready for furher action')

client.run(TOKEN)