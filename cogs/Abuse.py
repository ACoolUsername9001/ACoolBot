from discord.ext import commands
from main import ACoolBot
import discord
import json


def get_data(gid: int, name, default=None, data=json.load(open('data.json'))):
    try:
        return data[str(gid)][name]
    except KeyError:
        set_data(gid, name, default)
        return data[str(gid)][name]


def set_data(gid: int, name: str, val, data=json.load(open('data.json'))):
    try:
        data[str(gid)].update({name: val})
    except KeyError:
        data.update({str(gid): {name: val}})
    json.dump(data, open('data.json', 'w'))


def owner_check():
    def predicate(ctx: commands.Context):
        return ctx.message.author.id == 254671305268264960

    return commands.check(predicate)


class Abuse(commands.Cog):

    def __init__(self, bot: ACoolBot):
        self.bot = bot

    @commands.command(name='afk-purgatory', aliases=['ap'])
    @owner_check()
    async def afk_purgatory(self, ctx: commands.Context, *members: discord.Member):
        await ctx.message.delete()
        if members:
            for member in members:
                if member.voice.channel and member.voice.channel is not ctx.guild.afk_channel:
                    await member.move_to(ctx.guild.afk_channel)
                afk_purgatory = self.bot.get_data(ctx.guild.id, "afk purgatory", [])
                if member.id not in afk_purgatory:
                    afk_purgatory.append(member.id)
                else:
                    afk_purgatory.pop(afk_purgatory.index(member.id))
                self.bot.set_data(ctx.guild.id, "afk purgatory", afk_purgatory)

    @commands.command(name='say-in-channel', aliases=['sic'])
    @owner_check()
    async def say_in_channel(self, ctx: commands.Context, channel: discord.TextChannel, *args):
        message = ' '.join(args)
        if ctx.guild:
            await ctx.message.delete()
        await channel.send(message)

    @commands.command(name='move-channel', aliases=['mc'])
    @owner_check()
    async def move_channel(self, ctx: commands.Context, source: discord.VoiceChannel, dest: discord.VoiceChannel):
        members = source.members.copy()
        for member in members:
            if dest is not None:
                await member.move_to(dest)
        await ctx.message.delete()

    @commands.command(name='obliterate-but', aliases=['keep'])
    @owner_check()
    async def obliterate_but(self, ctx: commands.Context, number: int = 100, *members: discord.Member):
        if ctx.guild:
            await ctx.message.delete()
        logs = ctx.channel.history(limit=number)
        async for message in logs:
            if len(members) == 0 or (message.author not in members and message.author is not None):
                await message.delete()

    @commands.command(name='obliterate')
    @owner_check()
    async def obliterate(self, ctx: commands.Context, number: int = 100, *members: discord.Member):
        if ctx.guild:
            await ctx.message.delete()
        logs = ctx.channel.history(limit=number)
        async for message in logs:
            if len(members) == 0 or (message.author in members and message.author is not None):
                await message.delete()

    @commands.command(name='change-nickname', aliases=['cn'])
    @owner_check()
    async def change_nickname(self, ctx: commands.Context, member: discord.Member, nick: str):
        if ctx.guild:
            await ctx.message.delete()
        await member.edit(nick=nick)

    @commands.command(name='spam')
    @owner_check()
    async def spam(self, ctx: commands.Context, num: int, *args):
        message = ' '.join(args)
        await ctx.message.delete()
        for i in range(num):
            await ctx.send(message)

    @commands.command()
    @owner_check()
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        """Joins a voice channel"""

        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()

    @commands.command()
    @owner_check()
    async def leave(self, ctx):
        """Stops and disconnects the bot from voice"""

        await ctx.voice_client.disconnect()

    @commands.command(name="dump-data")
    @owner_check()
    async def dump_data(self, ctx: commands.Context):
        await ctx.send(str(self.bot.data))

    @commands.command(name="shuffle")
    @owner_check()
    async def shuffle(self, ctx: commands.Context):
        """ shuffles the people to different voice channels """
        members = []
        channels = ctx.guild.voice_channels
        for channel in channels:
            members += channel.members
        for member in members:
            allowed_channels = [channel for channel in channels if channel.permissions_for(member).connect or channel.permissions_for(member).read_messages]
            await member.move(random.choice(allowed_channels))


def setup(bot):
    bot.add_cog(Abuse(bot))
