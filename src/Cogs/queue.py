import logging
from collections import deque
from discord.ext import commands
import discord


class QueueCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.queue = deque(maxlen=15)

    def check_queue(self, ctx: commands.Context):
        # if queue is not empty
        if not self.queue:
            q = self.queue
            voice = ctx.guild.voice_client
            source = q.pop()
            voice.play(source)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self} connected to discord. ready for further action')

    @commands.command()
    async def q(self, ctx: commands.Context, url: str):
        try:
            audio_source = url
            source = discord.FFmpegPCMAudio(audio_source)
            self.queue.append(source)
            for elem in self.queue:
                print(elem)
        except Exception as e:
            logging.error('ERROR:' + str(e))

    @commands.command()
    async def qp(self, ctx: commands.Context):
        try:
            if not self.is_connected(ctx):
                voice_channel = ctx.author.voice.channel
                if not voice_channel:
                    return
                voice = await ctx.channel.connect()
            else:
                voice = ctx.guild.voice_client

            voice.play(self.queue.popleft(), after=lambda x=None: self.check_queue(ctx))
            voice.source = discord.PCMVolumeTransformer(voice.source)
            voice.source.volume = 1.0

        except Exception as e:
            logging.error(e)


async def setup(bot):
    await bot.add_cog(QueueCog(bot))
