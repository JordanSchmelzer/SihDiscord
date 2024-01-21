from discord.ext import commands
import json
import logging
import random


def validate_arg(arg, type="url"):
    if type == "url":
        if not "https://www.youtube.com/watch" in arg[0]:
            return False
    return True


class CommandsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self} connected to discord. ready for further action")

    @commands.command()
    async def emoji(self, ctx: commands.Context):
        try:
            await ctx.send(f"{self.bot.emojiList.false}")
        except Exception as e:
            print(e)

    @commands.command()
    async def my_playlist(self, ctx: commands.Context, arg1: str, *arg2: str):
        guild_id = ctx.message.guild.id
        msg_author = ctx.message.author.name

        if arg1 == "add":
            # check to see if arg2 is valid
            if validate_arg(arg2, type="url") == False:
                await ctx.send(
                    "Sorry, this is not a youtube watch url. Ex: https://www.youtube.com/watch?v=s-9aoZW1C-A&list=RDESnIQeYoWy8&index=4"
                )
                return

            try:
                # read json from a file to a dictionary
                with open("./src/data/playlists.json", "r") as f:
                    database = json.loads(f.read())

                # new user add method
                if msg_author in database.keys():
                    database[msg_author]["user_tracklist"]

                    # make users input into a dict
                    track_name = random.randint(2, 999999999)
                    new_track = {f"track{track_name}": arg2[0]}

                    # modify json data
                    database[msg_author]["user_tracklist"].update(new_track)
                    # stage changes, merge, update database
                    with open("./src/data/playlists.json", "w") as f:
                        json.dump(database, f, indent=4)
                else:
                    new_user = {f"{msg_author}": {"user_tracklist": {"track1": arg2}}}
                    print(f"Playlist created: {new_user}")
                    database.update(new_user)

                    with open("./src/data/playlists.json", "w") as f:
                        json.dump(database, f, indent=4)
            except Exception as e:
                print(e)

        if arg1 == "delete":
            try:
                index_to_delete = int(arg2[0]) - 1
                with open("./src/data/playlists.json", "r") as f:
                    database = json.loads(f.read())

                user_track_count = len(database[msg_author]["user_tracklist"])
                if int(arg2[0]) > user_track_count:
                    await ctx.send(
                        f"there are only {user_track_count} tracks. enter number of position track you need to delete."
                    )
                    return
                if int(arg2[0]) <= user_track_count:
                    key_list = list(database[msg_author]["user_tracklist"].keys())
                    database[msg_author]["user_tracklist"].pop(
                        key_list[index_to_delete]
                    )
                    print(database[msg_author]["user_tracklist"])

                    with open("./src/data/playlists.json", "w") as f:
                        json.dump(database, f, indent=4)
            except Exception as e:
                print(e)

        if arg1 == "size":
            try:
                with open("./src/data/playlists.json", "r") as f:
                    database = json.loads(f.read())

                user_track_count = len(database[msg_author]["user_tracklist"])

                await ctx.send(
                    f"Your playlist: {msg_author} has {user_track_count} songs"
                )

            except Exception as e:
                print(e)

        if arg1 == "list":
            # read json from a file to a dictionary
            try:
                with open("./src/data/playlists.json", "r") as f:
                    database = json.loads(f.read())

                track_list = []
                track_index = 0
                for track in database[msg_author]["user_tracklist"]:
                    track_index = track_index + 1
                    track_list.append(
                        f'Track_{track_index}:{database[msg_author]["user_tracklist"][track]}'
                    )
                await ctx.send("\n".join(track_list))
            except Exception as e:
                print(e)


async def setup(bot):
    await bot.add_cog(CommandsCog(bot))
