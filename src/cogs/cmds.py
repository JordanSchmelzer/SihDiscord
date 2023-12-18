import discord
from discord.ext import commands
from discord import FFmpegPCMAudio


class Cmds(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self} connected to discord. ready for further action')

    @commands.command()
    async def j(self, ctx):
        channel = ctx.author.voice.channel
        await ctx.channel.connect()

    @commands.command()
    async def lv(self, ctx):
        await ctx.voice_client.disconnect()

    @commands.command()
    async def r(self, ctx):
        print("i saw a message")
        await ctx.channel.send("response")

    @commands.command()
    async def p(self, ctx):
        channel = ctx.message.author.voice.channel
        print(channel)
        user = ctx.message.author
        print(user)
        vc = user.voice.channel
        print(vc)

        # download the YouTube video
        # don't actually do this, this breaks YouTube's TOS
        """
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
                if file != 'heading-south.mp3':
                    os.rename(file, "song.mp3")

        """
        # audio_source = 'song.mp3'

        audio_source = 'heading-south.mp3' # free use as long as credited, credit! freestockmusic.com
        voice_client = discord.utils.get(ctx.voice_clients, guild=ctx.guild)
        print(voice_client)

        if voice_client:
            await ctx.send('Saw !play, but already connected to another voice channel')
            return

        voice_channel = ctx.author.voice.channel
        voice_client = await voice_channel.connect()

        voice_client.play(discord.FFmpegPCMAudio(audio_source))


async def setup(bot):
    await bot.add_cog(Cmds(bot))
