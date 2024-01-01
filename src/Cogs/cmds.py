from discord.ext import commands
import discord

class CommandsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self} connected to discord. ready for further action')

    @commands.command()
    async def emoji(self, ctx: commands.Context):
        try:
            await ctx.send(f'{self.bot.emojiList.false}')
        except Exception as e:
            print(e)

    @commands.command()
    async def pt(self, ctx: commands.Context):
        try:
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
            except Exception as e:
                ctx.channel.disconnect()
                voice = await ctx.channel.connect()
            finally:
                voice.play(src, after=lambda e: print('Player error: %s' % e) if e else None)
                voice.source = discord.PCMVolumeTransformer(voice.source)
                voice.source.volume = 1.0
        except Exception as e:
            print(e)


async def setup(bot):
    await bot.add_cog(CommandsCog(bot))
