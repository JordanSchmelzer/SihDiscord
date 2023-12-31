import discord
from discord.ext import commands
# from Tools.Check import Check

class CogVolume(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self} connected to discord. ready for further action')

    @commands.command(name='v',
                      usage="<0 to 200>",
                      description='Modify the source volume level')
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def v(self, ctx: commands.Context, volume=None):

        if volume is None:
            return await ctx.send(f"{ctx.author.mention} This command requires an argument.\n Ex: !volume 30 (sets "
                                  f"the volume to 30% of source volume)")

        if (
                (not volume.isdigit()) or
                (int(volume)) < 0 or
                (int(volume) > 200)
        ):
            return await ctx.send(f"{ctx.author.mention} The volume have to be a number between 0 and 200!")

        # get the guild's VoiceClient
        voice_client = ctx.guild.voice_client
        print(voice_client)

        if voice_client.is_playing():
            print('is playing')

            new_volume = int(volume) / 100
            print({new_volume})

            voice_client.source = discord.PCMVolumeTransformer(voice_client.source, volume=new_volume)
            await ctx.send(f'Successfully set the volume to {volume}%')
        else:
            await ctx.send('The bot is not connected to a voice channel or is not playing audio.')


async def setup(bot):
    await bot.add_cog(CogVolume(bot))
