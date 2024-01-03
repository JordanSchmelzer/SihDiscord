from discord.ext import commands


class JoinLeaveCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self} connected to discord. ready for further action')

    @commands.command()
    async def join(self, ctx: commands.Context):
        await ctx.channel.connect()
        await ctx.send(f'Connected to {ctx.channel}')

    @commands.command()
    async def leave(self, ctx: commands.Context):
        await ctx.voice_client.disconnect()
        await ctx.send(f'Disconnected from {ctx.channel}')


async def setup(bot):
    await bot.add_cog(JoinLeaveCog(bot))
