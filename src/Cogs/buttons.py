import discord


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


class OptionButton(discord.ui.Button):
    def __init__(self, data: dict, row: str):
        ROWNUM = int(row)
        super().__init__(
            label=data["title"], style=discord.ButtonStyle.blurple, row=ROWNUM
        )
        self.value = data["id"]
        print(data["id"])

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "Adding Track to Queue", delete_after=10
        )
        try:
            # await interaction.delete_original_response()
            await interaction.message.delete()
            self.view.value = self.value
            self.view.stop()
        except Exception as e:
            print(e)


class OptionView(discord.ui.View):
    __slots__ = ("dict1", "dict2" "dict3")

    def __init__(self, args: dict):
        super().__init__()
        self.value = None  # this will store the button label
        self.dict1 = args[0]
        self.dict2 = args[1]
        self.dict3 = args[2]

        self.add_item(OptionButton(self.dict1, 1))
        self.add_item(OptionButton(self.dict2, 2))
        self.add_item(OptionButton(self.dict3, 3))

    @discord.ui.button(
        label="Cancel", style=discord.ButtonStyle.red, row=4, disabled=False, emoji="✖️"
    )
    async def close_callback(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.message.delete()
        self.stop()
        await interaction.rersponse.send_message("the view is stopped")
