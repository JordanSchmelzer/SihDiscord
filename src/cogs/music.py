from discord.ext import commands
import discord
import youtube_dl


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self} connected to discord. ready for further action')

    @commands.command()
    async def p(self, ctx):
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
        src = discord.FFmpegPCMAudio(audio_source)
        voice = await ctx.channel.connect()
        voice.play(src, after=lambda e: print('Player error: %s' % e) if e else None)
        voice.source = discord.PCMVolumeTransformer(voice.source)
        voice.source.volume = 1.0

    @commands.command()
    async def pause(self, ctx):
        server = ctx.message.guild
        voice = server.voice_client
        voice.pause()
        print('pause')

    @commands.command()
    async def resume(self, ctx):
        server = ctx.message.guild
        voice = server.voice_client
        voice.resume()
        print('resume')

# The setup function below is necessary. Remember we give bot.add_cog() the name of the class in this case MembersCog.
# When we load the cog, we use the name of the file.
async def setup(bot):
    await bot.add_cog(Music(bot))
