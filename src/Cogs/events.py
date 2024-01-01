from discord.ext import commands


class Events(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self} connected to discord. ready for further action')

    @commands.command()
    async def ping(self, ctx: commands.Context):
        await ctx.send("pong")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await member.create_dm()
        await member.dm_channel.send(
            f'Hello {member.name}, welcome to my DEV environment!'
        )


async def setup(bot):
    await bot.add_cog(Events(bot))
