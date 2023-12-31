from discord.ext import commands


class HelpCog(commands.Cog, name="help command"):
    def __init__(self, bot):
        self.bot = bot

    prefixes = ['$', '?', '.', '!']

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self} connected to discord. ready for further action')

    @commands.command()
    async def h(self, ctx: commands.Context, commandName=None):

        await ctx.channel.send(f"Here's a list of my commands:")

        if commandName is None:
            message0 = (f"""
            **command prefixes** = {self.prefixes}
            **{ctx.prefix}h <optional: command> :** Display the help list or the help data for a specific command.\n
            **{ctx.prefix}p <Url/Query> :** Search on youtube and play the music.
            **{ctx.prefix}j :** Add the bot to your voice channel.
            **{ctx.prefix}lv :** Remove the bot from your voice channel.
            **{ctx.prefix}pause :** Pause the current song.
            **{ctx.prefix}resume :** Resume the current song.
            **{ctx.prefix}volume <0-200> :** Change the bot's volume.
            """)

            message1 = (f"""
            **{self.bot.command_prefix}support :** Give a link to join the support server.
            **{self.bot.command_prefix}invite :** Give a link to invite the bot.
            **{self.bot.command_prefix}github :** Give the github link of the bot (source code).
            **{self.bot.command_prefix}vote :** Give the Top.gg link to vote for the bot.
            **{self.bot.command_prefix}search <Query> :** Search a song on youtube.
            **{self.bot.command_prefix}nowplaying :** Display data about the current song.
            **{self.bot.command_prefix}queue :** Display the queue.
            **{self.bot.command_prefix}move <IndexFrom> <IndexTo> :** Move a song in the queue.   
            """)

            message2 = (f"""
            **{self.bot.command_prefix}remove <Index> :** Remove the song with its index.
            **{self.bot.command_prefix}clear :** Clear the queue.
            **{self.bot.command_prefix}replay :** Replay the current song.
            **{self.bot.command_prefix}reload :** Reload the current song.
            **{self.bot.command_prefix}loop :** Enable or disable the loop mode.
            **{self.bot.command_prefix}loopqueue :** Enable or disable the loop queue mode.
            **{self.bot.command_prefix}playlist display :** Display playlist's songs.
            """)

            await ctx.channel.send(message0)
            # await ctx.channel.send(message1)
            # await ctx.channel.send(message2)


async def setup(bot):
    await bot.add_cog(HelpCog(bot))
