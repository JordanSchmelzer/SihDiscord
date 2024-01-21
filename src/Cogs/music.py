import asyncio
import logging
from asyncio import timeout
from discord.ext import commands
import discord
from functools import partial
import itertools
import sys
import traceback
from youtube_dl import YoutubeDL
from youtubesearchpython import VideosSearch
import json
import os


# define ydl console behavoir
def my_hook(d):
    if d["status"] == "finished":
        print("Done downloading, now converting ...")


ydl_opts = {
    "format": "bestaudio/best",
    "outtmpl": "./src/Songs/%(id)s.%(ext)s",
    "restrictfilenames": True,
    "noplaylist": True,
    "nocheckcertificate": True,
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }
    ],
    "ignoreerrors": False,
    "logtostderr": False,
    "quiet": True,
    "no_warnings": True,
    "default_search": "auto",
    "source_address": "0.0.0.0",  # ipv6 addresses cause issues sometimes
    #"proxy":"169.0.0.100:8080",
}

ffmpegopts = {"before_options": "-nostdin", "options": "-vn"}

ytdl = YoutubeDL(ydl_opts)


class VoiceConnectionError(commands.CommandError):
    """Custom Exception class for connection errors."""


class InvalidVoiceChannel(VoiceConnectionError):
    """Exception for cases of invalid Voice Channels."""


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, requester):
        super().__init__(source)
        self.requester = requester

        self.title = data.get("title")
        self.web_url = data.get("webpage_url")

        # YTDL info dicts (data) have other useful information you might want
        # https://github.com/rg3/youtube-dl/blob/master/README.md

    @classmethod
    async def create_source(cls, ctx, search: str, *, loop, download=True):
        print("[TRACE]: Youtube-DL: Creating Youtube Audio Source")
        loop = loop or asyncio.get_event_loop()

        # no_download_data
        no_data_to_run = partial(ytdl.extract_info, url=search, download=False)
        no_download_data = await loop.run_in_executor(None, no_data_to_run)

        if "entries" in no_download_data:
            no_download_data = no_download_data["entries"][0]

        # if not present, download it
        if os.path.exists(f'./src/Songs/{no_download_data["id"]}.mp3'):
            ytdl_download_opt = False
            
            await ctx.send(
                f'Added {no_download_data["title"]} to the Queue.', delete_after=15
            )
            
            source = f'./src/Songs/{no_download_data["id"]}.mp3'
            
            print(f"[TRACE]: Youtoube-DL: Audio already ripped: id={no_download_data["id"]}")

            return cls(
                discord.FFmpegPCMAudio(source),
                data=no_download_data,
                requester=ctx.author,
            )
        else:
            ytdl_download_opt = download
            to_run = partial(ytdl.extract_info, url=search, download=ytdl_download_opt)
            data = await loop.run_in_executor(None, to_run)

            if "entries" in data:
                # take first item from a playlist
                data = data["entries"][0]

            # TODO: clean this garbage up
            if download:
                # source = ytdl.prepare_filename(data)
                source = f'./src/Songs/{data["id"]}.mp3'
            else:
                return {
                    "webpage_url": data["webpage_url"],
                    "requester": ctx.author,
                    "title": data["title"],
                }
            print(f"[TRACE]: Youtube-DL: Audio Source Downloaded: id={data["id"]}")

            return cls(discord.FFmpegPCMAudio(source), data=data, requester=ctx.author)


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
        print('[TRACE]: Music player: bot is ready')

        while not self.bot.is_closed():
            self.next.clear()

            # Wait for the next song. If we timeout cancel the player and disconnect...
            try:
                
                async with timeout(DOWNLOAD_TIMEOUT):
                    print('[TRACE]: Music player: waiting for next song')
                    source = await self.queue.get()
                    print('[TRACE]: Music player: song ended, getting new song from queue')
                    
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

            # Make sure the FFmpeg process is cleaned up.
            source.cleanup()
            self.current = None

            try:
                # We are no longer playing this song...
                await self.np.delete()
            except discord.HTTPException:
                pass

    def destroy(self, guild):
        print(f'[TRACE]: Destroying Music Player attached to guild {guild}')
        """Disconnect and cleanup the player."""
        return self.bot.loop.create_task(self._cog.cleanup(guild))


class Music(commands.Cog):
    """Music related commands."""

    __slots__ = ("bot", "players")

    def __init__(self, bot):
        self.bot = bot
        self.players = {}

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self} connected to discord. ready for further action")

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

    @commands.command()
    async def join(
        self, ctx: commands.Context, *, channel: discord.VoiceChannel = None
    ):
        """Connect to voice.
        Parameters
        ------------
        channel: discord.VoiceChannel [Optional]
            The channel to connect to. If a channel is not specified, an attempt to join the voice channel you are in
            will be made.
        This command also handles moving the bot to different channels.
        """
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
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send(
                "I am not currently playing anything!", delete_after=20
            )

        await self.cleanup(ctx.guild)

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
    async def p(self, ctx: commands.Context, args):
        """Get a YouTube link from a query."""
        await ctx.send(f"Searching...", delete_after=10)

        links = VideosSearch(args, limit=3)

        print(links.result())


async def setup(bot):
    await bot.add_cog(Music(bot))
