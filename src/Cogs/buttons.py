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

        length = len(data["title"])
        # buttons cannot be longer than 80 bytes
        if length > 80:
            button_title = data["title"][0:80]
        else:
            button_title = data["title"]

        super().__init__(
            label=button_title, style=discord.ButtonStyle.blurple, row=ROWNUM
        )
        self.value = data["id"]
        print(data["id"])

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "Please wait... Adding track to queue...", delete_after=5
        )
        try:
            # await interaction.delete_original_response()
            await interaction.message.delete()
            self.view.value = (
                self.value
            )  # super important. sets the view to a value for logic in the calling funct
            self.view.stop()  # kills the view for higher function call. await i think
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
        self.value = "cancel"
        self.stop()
        # await interaction.rersponse.send_message("the view is stopped")
