from discord.ext import commands


class HelpCog(commands.Cog, name="help command"):
    def __init__(self, bot: commands.Bot):
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
            **{ctx.prefix}help :** Display the help list or the help data for a specific command.\n
            **{ctx.prefix}play <Url/Query> :** Search on youtube and play the music.
            **{ctx.prefix}join :** Add the bot to your voice channel.
            **{ctx.prefix}leave :** Remove the bot from your voice channel.
            **{ctx.prefix}pause :** Pause the current song.
            **{ctx.prefix}resume :** Resume the current song.
            **{ctx.prefix}stop :** Stops playing all audio and destroys the queue.
            **{ctx.prefix}volume <0-100> :** Change the bot's volume.
            **{ctx.prefix}queue_info :** Show the next 5 songs in queue.
            **{ctx.prefix}now_playing :** Show the current playing song
            **{ctx.prefix}skip :** Skip the current song in queue.
            """)

            await ctx.channel.send(message0)


async def setup(bot):
    await bot.add_cog(HelpCog(bot))
