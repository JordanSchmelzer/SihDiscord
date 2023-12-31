import discord
from discord.ext import commands


# from Tools.Check import Check

class CogPauseResume(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self} connected to discord. ready for further action')

    @commands.command()
    async def r(self, ctx: commands.Context):

        # get the guild's VoiceClient
        voice_client = ctx.guild.voice_client
        print(voice_client)

        # Check if the bot is connected to a voice channel and is playing audio
        if voice_client and voice_client.is_playing():
            voice_client.pause()
            await ctx.send('Audio has been paused.')
        else:
            await ctx.send('The bot is not connected to a voice channel or is not playing audio.')

    @commands.command()
    async def pt(self, ctx: commands.Context):

        audio_source = 'src/Songs/test.mp3'
        src = discord.FFmpegPCMAudio(audio_source)

        # ctx.author.voice returns a VoiceState object which contains information about hte member's voice connection status
        # if the member is connected to a voice channel, ctx.author.voice.channel will return the VoiceChannel object.
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await ctx.send(f'You are connected to {channel.name}')

        # How to see if bot is playing audio in a voice channel
        # VoiceClient.is_playing() method

        # get the guild's VoiceClient
        voice_client = ctx.guild.voice_client

        # check if the bot is connected to a voice channel
        if voice_client:
            if voice_client.is_playing():
                await ctx.send('The bot is playing audio.')
            else:
                await ctx.send('The bot is not playing audio.')
        else:
            await ctx.send('The bot is not connected to a voice channel.')

        try:
            voice = await ctx.channel.connect()
        except:
            ctx.channel.disconnect()
            voice = await ctx.channel.connect()
        finally:
            voice.play(src, after=lambda e: print('Player error: %s' % e) if e else None)
            voice.source = discord.PCMVolumeTransformer(voice.source)
            voice.source.volume = 1.0


async def setup(bot):
    await bot.add_cog(CogPauseResume(bot))
