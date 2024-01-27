from cls.youtube_downloader import *
from cls.youtube_metadata_fetcher import *
from Cogs.buttons import OptionView

from asyncio import timeout
from discord.ext import commands
from functools import partial
from youtubesearchpython import VideosSearch  # pip install python-video-search

import asyncio
import discord
import itertools
import json
import logging
import sys
import traceback


ffmpegopts = {"before_options": "-nostdin", "options": "-vn"}


class MusicPlayer:
    """A class which is assigned to each guild using the bot for Music.
    This class implements a queue and loop, which allows for different guilds to listen to different playlists
    simultaneously.
    When the bot disconnects from the Voice it's instance will be destroyed.
    """

    __slots__ = (
        "bot",
        "_guild",
        "_channel",
        "_cog",
        "queue",
        "next",
        "current",
        "np",
        "volume",
    )

    def __init__(self, ctx: commands.Context):
        MAX_SIZE = 50

        self.bot = ctx.bot
        self._guild = ctx.guild
        self._channel = ctx.channel
        self._cog = ctx.cog

        self.queue = asyncio.Queue(maxsize=MAX_SIZE)
        self.next = asyncio.Event()

        self.np = None  # Now playing message
        self.volume = 0.5
        self.current = None

        ctx.bot.loop.create_task(self.player_loop())

    async def player_loop(self):
        DOWNLOAD_TIMEOUT = 300

        """Our main player loop."""
        await self.bot.wait_until_ready()
        print("[TRACE]: Music player: bot is ready")

        while not self.bot.is_closed():
            self.next.clear()

            # Wait for the next song. If we timeout cancel the player and disconnect...
            try:
                async with timeout(DOWNLOAD_TIMEOUT):
                    print("[TRACE]: Music player: waiting for next song")
                    source = await self.queue.get()
            except asyncio.TimeoutError:
                print(f"[FATAL]: exceeded timeout limit of {DOWNLOAD_TIMEOUT}")
                return self.destroy(self._guild)

            self.current = source
            source.volume = self.volume

            print(f"[TRACE]: Music player: playing {source}")
            self._guild.voice_client.play(
                source,
                after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set),
            )
            self.np = await self._channel.send(
                f"**Now Playing:** `{source.title}` requested by "
                f"`{source.requester}`"
            )
            await self.next.wait()

            source.cleanup()  # Make sure the FFmpeg process is cleaned up.
            self.current = None

            try:
                await self.np.delete()  # We are no longer playing this song...
            except discord.HTTPException:
                pass

    def destroy(self, guild):
        print(f"[TRACE]: Destroying Music Player attached to guild {guild}")
        """Disconnect and cleanup the player."""
        return self.bot.loop.create_task(self._cog.cleanup(guild))


class Music(commands.Cog):
    """Music related commands."""

    __slots__ = ("bot", "players")

    def __init__(self, bot):
        self.bot = bot
        self.players = {}

    async def cleanup(self, guild: commands.Context.guild):
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass

        try:
            del self.players[guild.id]
        except KeyError:
            pass

    async def __local_check(self, ctx: commands.Context):
        """A local check which applies to all commands in this cog."""
        if not ctx.guild:
            raise commands.NoPrivateMessage
        return True

    async def __error(self, ctx: commands.Context, error):
        """A local error handler for all errors arising from commands in this cog."""
        if isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.send(
                    "This command can not be used in Private Messages."
                )
            except discord.HTTPException:
                pass
        elif isinstance(error, InvalidVoiceChannel):
            await ctx.send(
                "Error connecting to Voice Channel. "
                "Please make sure you are in a valid channel or provide me with one"
            )

        print("Ignoring exception in command {}:".format(ctx.command), file=sys.stderr)
        traceback.print_exception(
            type(error), error, error.__traceback__, file=sys.stderr
        )

    def get_player(self, ctx: commands.Context):
        """Retrieve the guild player, or generate one."""
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = MusicPlayer(ctx)
            self.players[ctx.guild.id] = player

        return player

    async def join(
        self, ctx: commands.Context, *, channel: discord.VoiceChannel = None
    ):
        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                raise InvalidVoiceChannel(
                    "No channel to join. Please either specify a valid channel or join one."
                )

        vc = ctx.voice_client

        if vc:
            if vc.channel.id == channel.id:
                return
            try:
                await vc.move_to(channel)
            except asyncio.TimeoutError:
                raise VoiceConnectionError(f"Moving to channel: <{channel}> timed out.")
        else:
            try:
                await channel.connect()
            except asyncio.TimeoutError:
                raise VoiceConnectionError(
                    f"Connecting to channel: <{channel}> timed out."
                )

        await ctx.send(f"Connected to: **{channel}**", delete_after=20)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self} connected to discord. ready for further action")

    @commands.command()
    async def play(self, ctx: commands.Context, *, search: str):
        """Request a song and add it to the queue.
        Uses YTDL to automatically search and retrieve a song.
        Parameters
        ------------
        search: str [Required]
            The song to search and retrieve using YTDL. This could be a simple search, an ID or URL.
            :param search:
            :param ctx:
        """

        await ctx.typing()

        vc = ctx.voice_client

        if not vc:
            await ctx.invoke(self.join)

        """Retrieve the guild player, or generate one."""
        player = self.get_player(ctx)

        # If download is False, source will be a dict which will be used later to regather the stream.
        # If download is True, source will be a discord.FFmpegPCMAudio with a VolumeTransformer.
        source = await YTDLSource.create_source(
            ctx, search, loop=self.bot.loop, download=True
        )

        await player.queue.put(source)

    @commands.command()
    async def pause(self, ctx):
        """Pause the currently playing song."""
        vc = ctx.voice_client

        if not vc or not vc.is_playing():
            return await ctx.send(
                "I am not currently playing anything!", delete_after=20
            )
        elif vc.is_paused():
            return

        vc.pause()
        await ctx.send(f"**`{ctx.author}`**: Paused the song!")

    @commands.command()
    async def resume(self, ctx):
        """Resume the currently paused song."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send(
                "I am not currently playing anything!", delete_after=20
            )
        elif not vc.is_paused():
            return

        vc.resume()
        await ctx.send(f"**`{ctx.author}`**: Resumed the song!")

    @commands.command()
    async def skip(self, ctx):
        """Skip the song."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send(
                "I am not currently playing anything!", delete_after=20
            )

        if vc.is_paused():
            pass
        elif not vc.is_playing():
            return

        vc.stop()
        await ctx.send(f"**`{ctx.author}`**: Skipped the song!")

    @commands.command()
    async def queue_info(self, ctx):
        """Retrieve a basic queue of upcoming songs."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send(
                "I am not currently connected to voice!", delete_after=20
            )

        player = self.get_player(ctx)
        if player.queue.empty():
            return await ctx.send("There are currently no more queued songs.")

        # Grab up to 5 entries from the queue...
        upcoming = list(itertools.islice(player.queue._queue, 0, 5))

        fmt = "\n".join(f"{obj.title}" for obj in upcoming)
        embed = discord.Embed(title=f"Upcoming - Next {len(upcoming)}", description=fmt)

        await ctx.send(embed=embed)

    @commands.command()
    async def now_playing(self, ctx):
        """Display information about the currently playing song."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send(
                "I am not currently connected to voice!", delete_after=20
            )

        player = self.get_player(ctx)
        if not player.current:
            return await ctx.send("I am not currently playing anything!")

        try:
            # Remove our previous now_playing message.
            await player.np.delete()
        except discord.HTTPException:
            pass

        player.np = await ctx.send(
            f"**Now Playing:** `{vc.source.title}` "
            f"requested by `{vc.source.requester}`"
        )

    @commands.command()
    async def volume(self, ctx: commands.Context, vol: float):
        """Change the player volume.
        Parameters
        ------------
        volume: float or int [Required]
            The volume to set the player to in percentage. This must be between 1 and 100.
        """
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send("Im not connected to voice!", delete_after=20)

        if not 0 < vol < 101:
            return await ctx.send("Please enter a value between 1 and 100.")

        player = self.get_player(ctx)

        if vc.source:
            vc.source.volume = vol / 100

        player.volume = vol / 100
        await ctx.send(f"**`{ctx.author}`**: Set the volume to **{vol}%**")

    @commands.command()
    async def stop(self, ctx: commands.Context):
        """Stop the currently playing song and destroy the player.
        !Warning!
        This will destroy the player assigned to your guild, also deleting any queued songs and settings.
        """
        try:
            vc = ctx.voice_client
            if not vc or not vc.is_connected():
                return await ctx.send(
                    "I am not currently playing anything!", delete_after=20
                )
            await self.cleanup(ctx.guild)
            print(f"[warn][music] method stop has stopped the player and left voice")
        except Exception as e:
            print(f"[fatal][music] method stop failed for exception:{e}")

    @commands.command()
    async def playlist(self, ctx: commands.Context):
        try:
            author = ctx.message.author.name
            guild_id = ctx.message.guild.id

            with open("./src/data/playlists.json", "r") as f:
                database = json.loads(f.read())

            tracks = {}
            tracks = database[author]["user_tracklist"]

            vc = ctx.voice_client

            if not vc:
                await ctx.invoke(self.join)
                """Retrieve the guild player, or generate one."""

            player = self.get_player(ctx)

            for track in tracks:
                # If download is False, source will be a dict which will be used later to regather the stream.
                # If download is True, source will be a discord.FFmpegPCMAudio with a VolumeTransformer.
                track_to_load: str
                track_to_load = tracks[track]
                print(track_to_load)

                source = await YTDLSource.create_source(
                    ctx, track_to_load, loop=self.bot.loop, download=True
                )
                await player.queue.put(source)
        except Exception as e:
            logging.fatal(e)

    @commands.command()
    async def search(self, ctx: commands.Context, args):
        """
        Getting information about video or its formats using video link or video ID.

        `Video.get` method will give both information & formats of the video
        `Video.getInfo` method will give only information about the video.
        `Video.getFormats` method will give only formats of the video.

        You may either pass link or ID, method will take care itself.

        YouTube doesn't provide uploadDate and publishDate in its InnerTube API, thus we have to use HTML requests to get it.
        This is disabled by default as it is very inefficient, but if you really need it, you can explicitly set parameter to Video.get() function: get_upload_date=True
        By default, we use InnerTube API for Video.get() and Video.getFormats(), meanwhile we use HTML parsing on Video.getInfo()
        You can set get_upload_date ONLY TO Video.get(), as you don't get info with Video.getFormats()


        video = Video.get('https://www.youtube.com/watch?v=z0GKGpObgPY', mode = ResultMode.json, get_upload_date=True)
        print(video)
        videoInfo = Video.getInfo('https://youtu.be/z0GKGpObgPY', mode = ResultMode.json)
        print(videoInfo)
        videoFormats = Video.getFormats('z0GKGpObgPY')
        print(videoFormats)
        """

        LIMIT = 3
        data = {}
        await ctx.send(f"Searching...", delete_after=3)
        try:
            video_search = VideosSearch(args, limit=LIMIT, region="US")
            data = video_search.result()
            # for debug only
            # with open("./src/data/video_data.json", "w") as f:
            # json.dump(data,f, indent=4)
            i = 0
            result_dict = {}
            while i <= (LIMIT - 1):
                data_id = data["result"][i]["id"]
                data_title = data["result"][i]["title"]
                data_duration = data["result"][i]["duration"]
                data_views = data["result"][i]["viewCount"]["text"]
                this_result_dict = {
                    "id": data_id,
                    "title": data_title,
                    "duration": data_duration,
                    "views": data_views,
                }
                result_dict[i] = this_result_dict
                i = i + 1

            menu_view = OptionView(result_dict)
            await ctx.send(view=menu_view, delete_after=60)
            try:
                await menu_view.wait()
                print(menu_view.value)
                # await ctx.typing()
            except Exception as e:
                print(e)

            vc = ctx.voice_client
            if not vc:
                await ctx.invoke(self.join)

            player = self.get_player(ctx)  # Retrieve the guild player, or generate one.
            source = await YTDLSource.create_source(
                ctx, menu_view.value, loop=self.bot.loop, download=True
            )
            await player.queue.put(source)

        except Exception as e:
            print(e)


async def setup(bot):
    await bot.add_cog(Music(bot))
