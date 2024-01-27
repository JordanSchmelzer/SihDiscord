from discord.ext import commands


class YoutubeSearchHandler:
    __slots__ = ("bot", "foo", "data")

    def __init__(self, ctx: commands.Context):
        __bot__ = self.bot
        print(__bot__)
        __data__ = {}

    @classmethod
    async def create_source(cls, ctx, search: str, *, loop, download=True, __data__):
        print("[TRACE]: YoutubeSearch: searching for top 3 results")

        return __data__
