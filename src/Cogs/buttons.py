import discord
from discord.ext import commands


class InviteButtons(discord.ui.View):
    def __init__(self, inv: str):
        super().__init()
        self.inv = inv
        self.add_item(discord.ui.Button(label="Some Link", url=self.inv))

    @discord.ui.button(label="Invite button", style=discord.ButtonStyle.blurple)
    async def inviteBtn(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        # basically ctx.send
        await interaction.rersponse.send_message(self.inv, ephemeral=True)


@bot.command()
async def invite(ctx: commands.Context):
    inv = await ctx.channel.create_invite()
    await ctx.send("Click the button", view=InviteButtons(str(inv)))
