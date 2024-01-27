import discord
import asyncio
import os
from functools import partial
from youtube_dl import (
    YoutubeDL,
)  # import youtube_dl pip install git+https://github.com/ytdl-org/youtube-dl.git@master#egg=youtube_dl

 # YTDL info dicts (data) have other useful information you might want
# https://github.com/rg3/youtube-dl/blob/master/README.md


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
    # "proxy":"169.0.0.100:8080",
}

ytdl = YoutubeDL(ydl_opts)

# define ydl console behavoir
def my_hook(d):
    if d["status"] == "finished":
        print("Done downloading, now converting ...")

class YTDLSource(discord.PCMVolumeTransformer):
    __slots__ = ("requester","title","web_url")
    
    def __init__(self, source, *, data, requester):
        super().__init__(source)
        self.requester = requester
        self.title = data.get("title")
        self.web_url = data.get("webpage_url")
 
    @classmethod
    async def create_source(cls, ctx, search: str, *, loop, download=True):
        print("[trace][youtube-dl]: Creating Youtube Audio Source")
        loop = loop or asyncio.get_event_loop()

        # no_download_data
        no_data_to_run = partial(ytdl.extract_info, url=search, download=False)
        no_download_data = await loop.run_in_executor(None, no_data_to_run)

        # stops playlists i think
        if "entries" in no_download_data:
              no_download_data = no_download_data["entries"][0]

        # if not present download it, else use existing resource
        if os.path.exists(f'./src/Songs/{no_download_data["id"]}.mp3'):
            ytdl_download_opt = False
            
            await ctx.send(
                f'Added {no_download_data["title"]} to the Queue.', delete_after=2
            )
            
            source = f'./src/Songs/{no_download_data["id"]}.mp3'
            print(f"[trace][youtube-dl]: video id found in songs/: id={no_download_data["id"]}")

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
            print(f"[trace][youtube-dl]: video audio downloaded as mp3 in songs/: id={data["id"]}")

            return cls(discord.FFmpegPCMAudio(source), data=data, requester=ctx.author)

