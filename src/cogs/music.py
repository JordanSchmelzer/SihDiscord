from discord.ext import commands
import discord
import youtube_dl
import os


def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')


class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self} connected to discord. ready for further action')

    @commands.command()
    async def p(self, ctx, url: str):
        ydl_opts = {
            'format': 'bestaudio/best',
            'extractaudio': True,
            'noplaylist': True,
            'nocheckcertificate': True,
            'logtostderr': False,
            'ignoreerrors': False,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'no_warnings': True,
            'logger': MyLogger(),
            'progress_hooks': [my_hook],
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        for file in os.listdir('./'):
            print(file)

        path = './'
        dest = 'src/songs/that.mp3'
        for file in os.listdir(path):
            if file.endswith(".mp3"):
                print(file)
                os.rename(path + file, dest)

        audio_source = dest
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
