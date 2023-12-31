from discord.ext import commands


class CommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self} connected to discord. ready for further action')

    @commands.command()
    async def j(self, ctx: commands.Context):
        await ctx.channel.connect()
        await ctx.send(f'Connected to {ctx.channel}')

    @commands.command()
    async def lv(self, ctx: commands.Context):
        await ctx.voice_client.disconnect()
        await ctx.send(f'Disconnected from {ctx.channel}')


async def setup(bot):
    await bot.add_cog(CommandsCog(bot))
