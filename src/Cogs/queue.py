from discord.ext import commands


class QueueCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self} connected to discord. ready for further action')

    @commands.command()
    async def queue(self, ctx: commands.Context):
        print(ctx.bot.activity)


async def setup(bot):
    await bot.add_cog(QueueCog(bot))
