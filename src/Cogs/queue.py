import logging
from collections import deque
from discord.ext import commands
import discord


class QueueCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.data = []

    def add_data(self, data):
        self.data.append(data)

    def get_data(self):
        return self.data

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self} connected to discord. ready for further action')

    @commands.command()
    async def q(self, ctx: commands.Context):
        try:
            # voice = ctx.guild.voice_client
            audio_source = 'src/Songs/song.mp3'
            source = discord.FFmpegPCMAudio(audio_source)

            guild_id = ctx.message.guild.id
            logging.info(guild_id)

            # if guild_id in self.data:
                # self.data[guild_id].add_data(1)
            # else:
                # self.data[guild_id].add_data(2)

            self.data.append(source)

            for element in self.data:
                print(element)

        except Exception as e:
            logging.error('Error:' + str(e))


async def setup(bot):
    await bot.add_cog(QueueCog(bot))
