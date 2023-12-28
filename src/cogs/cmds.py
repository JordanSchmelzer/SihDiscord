import discord
import youtube_dl
from discord.ext import commands
from discord import FFmpegPCMAudio


class CommandsCog(commands.Cog):
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
    async def p(self, ctx):
        print("running command p")

        '''
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        }
        print("done setting ydl options")
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            print('im downloading')
        for file in os.listdir("./"):
            if file.endswith(".mp3"):
                if file != 'song.mp3':
                    os.rename(file, "song.mp3")
                    print('i renamed the file')
        '''

        audio_source = 'src/cogs/song.mp3'  # free use as long as credited, credit! freestockmusic.com
        voice = await ctx.channel.connect()
        src = discord.FFmpegPCMAudio(str())
        print(voice)
        voice.play(discord.FFmpegPCMAudio(audio_source))
        print("im done playing")


# The setup function below is necessary. Remember we give bot.add_cog() the name of the class in this case MembersCog.
# When we load the cog, we use the name of the file.
async def setup(bot):
    await bot.add_cog(CommandsCog(bot))
