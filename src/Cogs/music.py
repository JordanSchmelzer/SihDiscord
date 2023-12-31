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
    async def p(self, ctx: commands.Context, url: str):
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

        # for file in os.listdir('./'):
            # print(file)

        path = './'
        audio_source = 'src/Songs/song.mp3'
        for file in os.listdir(path):
            if file.endswith(".mp3"):
                if os.path.exists(audio_source):
                    print('INFO: removing old audio source')
                    os.remove(audio_source)
                    os.rename(path + file, audio_source)
                    print('INFO: renamed download to Songs/song.mp3')
                else:
                    os.rename(path + file, audio_source)
                    print('INFO: renamed download to Songs/song.mp3')

        src = discord.FFmpegPCMAudio(audio_source)

        voice_channel = ctx.author.voice.channel
        print(f'INFO: authors voice channel is: {voice_channel}')
        voice_client = ctx.guild.voice_client
        print(f'INFO: guild voice client is: {voice_client}')

        try:
            # Check if the bot is connected to a voice channel
            if voice_client and voice_client.channel == voice_channel:
                print('The bot is already connected to the voice channel.')
                voice_client.play(src, after=lambda e: print('Player error: %s' % e) if e else None)
                voice_client.source = discord.PCMVolumeTransformer(voice_client.source)
                voice_client.source.volume = 1.0
            else:
                # Connect to the voice channel
                voice_client = await voice_channel.connect()
                print('The bot has connected to the voice channel.')
                voice_client.play(src, after=lambda e: print('Player error: %s' % e) if e else None)
                voice_client.source = discord.PCMVolumeTransformer(voice_client.source)
                voice_client.source.volume = 1.0

        except Exception as e:
            print(e)

        print('TRACE: End <prefix>p')

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
