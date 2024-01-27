import asyncio
import discord
import logging
from discord.ext import commands


class VoiceConnectionError(commands.CommandError):
    """Custom Exception class for connection errors."""


class InvalidVoiceChannel(VoiceConnectionError):
    """Exception for cases of invalid Voice Channels."""


class JoinLeaveCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cleanup(self, guild: commands.Context.guild):
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass

        try:
            del self.players[guild.id]
        except KeyError:
            pass

    @commands.command()
    async def leave(self, ctx: commands.Context):
        """Stop the currently playing song and destroy the player.
        This will destroy the player assigned to your guild, also deleting any queued songs and settings.
        """
        try:
            vc = ctx.voice_client
            if not vc or not vc.is_connected():
                return await ctx.send("Not in voice.", delete_after=1.5)
            await self.cleanup(ctx.guild)
        except Exception as e:
            logging.fatal(f"[fatal][joinleave]: method leave failed for exception:{e}")

    @commands.command()
    async def join(
        self, ctx: commands.Context, *, channel: discord.VoiceChannel = None
    ):
        """Connect to voice.
        Parameters
        ------------
        channel: discord.VoiceChannel [Optional] The channel to connect to.
        If a channel is not specified, an attempt to join the voice channel you are in will be made.
        This command also handles moving the bot to different channels.
        """
        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                raise InvalidVoiceChannel(
                    "No channel to join. Please either specify a valid channel or join one."
                )

        vc = ctx.voice_client

        if vc:
            if vc.channel.id == channel.id:
                return
            try:
                await vc.move_to(channel)
            except asyncio.TimeoutError:
                raise VoiceConnectionError(f"Moving to channel: <{channel}> timed out.")
        else:
            try:
                await channel.connect()
            except asyncio.TimeoutError:
                raise VoiceConnectionError(
                    f"Connecting to channel: <{channel}> timed out."
                )

        await ctx.send(f"Connected to: **{channel}**", delete_after=20)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self} connected to discord. ready for further action")


async def setup(bot):
    await bot.add_cog(JoinLeaveCog(bot))
