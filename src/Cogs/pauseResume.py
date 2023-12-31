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
    async def pause(self, ctx: commands.Context):
        server = ctx.message.guild
        voice = server.voice_client
        if voice.is_playing():
            voice.pause()
            print('pause')
            await ctx.send('track paused')

    @commands.command()
    async def resume(self, ctx: commands.Context):
        server = ctx.message.guild
        voice = server.voice_client
        if voice.is_paused():
            voice.resume()
            print('resume')
            await ctx.send('resuming track')

    @commands.command()
    async def stop(self, ctx: commands.Context):
        server = ctx.message.guild
        voice = server.voice_client
        if voice.is_paused() or voice.is_playing():
            voice.stop()
            print('stop')
            await ctx.send('stopped playing track')

async def setup(bot):
    await bot.add_cog(CogPauseResume(bot))
