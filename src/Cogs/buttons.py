import discord
from discord.ext import commands


class InviteButtons(discord.ui.View):
    buttons = [
        Button(style=ButtonStyle.grey, label="1"),
        Button(style=ButtonStyle.grey, label="2"),
        Button(style=ButtonStyle.grey, label="3"),
        Button(style=ButtonStyle.grey, label="x"),
        Button(style=ButtonStyle.red, label="Exit"),
    ]
