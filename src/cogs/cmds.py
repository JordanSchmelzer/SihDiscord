from discord.ext import commands


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


async def setup(bot):
    await bot.add_cog(CommandsCog(bot))
