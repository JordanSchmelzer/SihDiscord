from discord.ext import commands
from Cogs.buttons import InviteButtons


class InviteCog(commands.Cog):
    __slots__ = "bot"

    def __init__(self, bot: commands.Bot):
        __bot__ = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self} connected to discord. ready for further action")

    @commands.command()
    async def invite(self, ctx: commands.Context):
        inv = await ctx.channel.create_invite()
        # await ctx.send("Click the button", view=InviteButtons(str(inv)))
        # buttons_obj = InviteButtons(inv)
        await ctx.send(inv)


async def setup(bot):
    await bot.add_cog(InviteCog(bot))
