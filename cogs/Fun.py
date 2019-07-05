import random
from discord.ext import commands
from main import ACoolBot
import discord
from discord.ext.commands import BucketType

import colorsys

# def cooldown_check(amount, time, bucketType):
#     cd = commands.CooldownMapping.from_cooldown(amount, time, bucketType)
#
#     def predicate(ctx: commands.Context):
#         bucket = cd.get_bucket(ctx.message)
#         retry_after = bucket.update_rate_limit()
#         admin = discord.utils.find(lambda r: r.name == 'Admin' or r.permissions.administrator, ctx.author.roles)
#         if admin:
#             if retry_after:
#                 retry_after -= 3*time/4
#                 if retry_after < 0:
#                     retry_after = 0
#                     bucket.reset()
#
#         if ctx.author.id == 254671305268264960:
#             retry_after = 0
#             bucket.reset()
#
#         if retry_after:
#             raise commands.errors.CommandOnCooldown(bucket, retry_after)
#
#         return not retry_after
#
#     return commands.check(predicate)


def owner_check():
    def predicate(ctx: commands.Context):
          return ctx.message.author.id == 254671305268264960
    return commands.check(predicate)


class Fun(commands.Cog):

    def __init__(self, bot: ACoolBot):
        self.bot = bot
        self.pages = {}

    @commands.command(name='roll')
    async def roll(self, ctx: commands.Context, *dice: str):
        results = {}
        for d in dice:
            quantity, faces = d.split('d')
            faces = int(faces)
            results.update({faces: []})
            for _ in range(int(quantity)):
                results[faces].append(random.randint(1, faces))
        embed = discord.Embed(title='**__Rolled:__**', color=999900, type="rich")
        for faces, dice in results.items():
            embed.add_field(name="**" + str(faces) + ":**", value=', '.join(str(d) for d in dice), inline=False)
        await ctx.send(embed=embed)

    @commands.command(name='cheat_roll', aliases=['Roll'], hidden=True)
    async def cheat_roll(self, ctx: commands.Context, *dice: str):
        results = {}
        for d in dice:
            quantity, faces = d.split('d')
            faces = int(faces)
            randomize = faces // 10
            results.update({faces: []})
            for _ in range(int(quantity)):
                if ctx.author.id == 254671305268264960:
                    results[faces].append(faces-random.randint(0, randomize))
                else:
                    results[faces].append(random.randint(1, faces))
        embed = discord.Embed(title='**__Rolled:__**', color=999900, type="rich")
        for faces, dice in results.items():
            embed.add_field(name="**" + str(faces) + ":**", value=', '.join(str(d) for d in dice), inline=False)
        await ctx.send(embed=embed)

    @commands.command(name='say', hidden=True)
    @owner_check()
    async def say(self, ctx: commands.Context, *string: str):
        await ctx.message.delete()
        await ctx.send(' '.join(string))

    @commands.command(name='!rank*')
    @owner_check()
    async def rank(self, ctx: commands.Context):
        file = discord.File('cogs/card.png')
        await ctx.send(file=file)

    @commands.command(name="accept", hidden=True)
    async def accept(self, ctx: commands.Context):
        accept_role = ctx.guild.get_role(542308860937895949)
        if accept_role and accept_role not in ctx.author.roles:
            await ctx.author.add_roles(accept_role)
            await ctx.author.send("By using this command you agreed to being fully aware of the rules")

    @commands.command(name='big', aliases=['BIG', 'b', 'B'])
    # @cooldown_check(1, 300, BucketType.user)
    async def big(self, ctx: commands.Context, *string: str):
        string = ' '.join(string).upper()
        if string[0] in 'אבגדהוזחטיכלמנסעפצקרשתץךףםן':
            string = string[::-1]
        numbers = {
            '0': [

                '▓▓▓▓▓▓▓',
                '▓░░░░░▓',
                '▓░▓▓▓░▓',
                '▓░▓▓▓░▓',
                '▓░▓▓▓░▓',
                '▓░░░░░▓',
                '▓▓▓▓▓▓▓'],

            '1': [

                '▓▓▓▓▓▓',
                '▓▓░░▓▓',
                '▓░▓░▓▓',
                '▓▓▓░▓▓',
                '▓▓▓░▓▓',
                '▓░░░░▓',
                '▓▓▓▓▓▓'],

            '2': [

                '▓▓▓▓▓▓▓',
                '▓░░░░░▓',
                '▓▓▓▓▓░▓',
                '▓░░░░░▓',
                '▓░▓▓▓▓▓',
                '▓░░░░░▓',
                '▓▓▓▓▓▓▓'],

            '3': [

                '▓▓▓▓▓▓▓',
                '▓░░░░░▓',
                '▓▓▓▓▓░▓',
                '▓░░░░░▓',
                '▓▓▓▓▓░▓',
                '▓░░░░░▓',
                '▓▓▓▓▓▓▓'],

            '4': [

                '▓▓▓▓▓▓▓',
                '▓▓▓░░▓▓',
                '▓▓░▓░▓▓',
                '▓░▓▓░▓▓',
                '▓░░░░░▓',
                '▓▓▓▓░▓▓',
                '▓▓▓▓▓▓▓'],

            '5': [

                '▓▓▓▓▓▓▓',
                '▓░░░░░▓',
                '▓░▓▓▓▓▓',
                '▓░░░░░▓',
                '▓▓▓▓▓░▓',
                '▓░░░░░▓',
                '▓▓▓▓▓▓▓'],

            '6': [
                '▓▓▓▓▓▓▓',
                '▓░░░░░▓',
                '▓░▓▓▓▓▓',
                '▓░░░░░▓',
                '▓░▓▓▓░▓',
                '▓░░░░░▓',
                '▓▓▓▓▓▓▓'],

            '7': [

                '▓▓▓▓▓▓▓',
                '▓░░░░░▓',
                '▓▓▓▓▓░▓',
                '▓▓▓▓░▓▓',
                '▓▓▓░▓▓▓',
                '▓▓░▓▓▓▓',
                '▓▓▓▓▓▓▓'],

            '8': [

                '▓▓▓▓▓▓▓',
                '▓░░░░░▓',
                '▓░▓▓▓░▓',
                '▓░░░░░▓',
                '▓░▓▓▓░▓',
                '▓░░░░░▓',
                '▓▓▓▓▓▓▓'],

            '9': [

                '▓▓▓▓▓▓▓',
                '▓░░░░░▓',
                '▓░▓▓▓░▓',
                '▓░░░░░▓',
                '▓▓▓▓▓░▓',
                '▓░░░░░▓',
                '▓▓▓▓▓▓▓'],
            ' ': [

                '▓▓▓▓',
                '▓▓▓▓',
                '▓▓▓▓',
                '▓▓▓▓',
                '▓▓▓▓',
                '▓▓▓▓',
                '▓▓▓▓'],

            'A': [

                '▓▓▓▓▓▓▓',
                '▓▓░░░▓▓',
                '▓░▓▓▓░▓',
                '▓░░░░░▓',
                '▓░▓▓▓░▓',
                '▓░▓▓▓░▓',
                '▓▓▓▓▓▓▓'],
            'B': [

                '▓▓▓▓▓▓▓',
                '▓░░░░▓▓',
                '▓░▓▓▓░▓',
                '▓░░░░▓▓',
                '▓░▓▓▓░▓',
                '▓░░░░▓▓',
                '▓▓▓▓▓▓▓'],
            'C': [

                '▓▓▓▓▓▓▓',
                '▓▓░░░░▓',
                '▓░░▓▓▓▓',
                '▓░░▓▓▓▓',
                '▓░░▓▓▓▓',
                '▓▓░░░░▓',
                '▓▓▓▓▓▓▓'],
            'D': [

                '▓▓▓▓▓▓▓',
                '▓░░░░▓▓',
                '▓░▓▓▓░▓',
                '▓░▓▓▓░▓',
                '▓░▓▓▓░▓',
                '▓░░░░▓▓',
                '▓▓▓▓▓▓▓'],
            'E': [

                '▓▓▓▓▓▓▓',
                '▓░░░░░▓',
                '▓░░▓▓▓▓',
                '▓░░░░░▓',
                '▓░░▓▓▓▓',
                '▓░░░░░▓',
                '▓▓▓▓▓▓▓'],
            'F': [

                '▓▓▓▓▓▓▓',
                '▓░░░░░▓',
                '▓░░▓▓▓▓',
                '▓░░░░░▓',
                '▓░░▓▓▓▓',
                '▓░░▓▓▓▓',
                '▓▓▓▓▓▓▓'],
            'G': [

                '▓▓▓▓▓▓▓',
                '▓▓░░░▓▓',
                '▓░░▓▓▓▓',
                '▓░░▓░░▓',
                '▓░░▓▓░▓',
                '▓▓░░░▓▓',
                '▓▓▓▓▓▓▓'],
            'H': [

                '▓▓▓▓▓▓▓▓',
                '▓░░▓▓░░▓',
                '▓░░▓▓░░▓',
                '▓░░░░░░▓',
                '▓░░▓▓░░▓',
                '▓░░▓▓░░▓',
                '▓▓▓▓▓▓▓▓'],
            'I': [

                '▓▓▓▓',
                '▓░░▓',
                '▓░░▓',
                '▓░░▓',
                '▓░░▓',
                '▓░░▓',
                '▓▓▓▓'],
            'J': [

                '▓▓▓▓▓▓▓',
                '▓░░░░░▓',
                '▓▓▓▓░▓▓',
                '▓▓▓▓░▓▓',
                '▓░▓▓░▓▓',
                '▓▓░░▓▓▓',
                '▓▓▓▓▓▓▓'],
            'K': [

                '▓▓▓▓▓▓',
                '▓░▓▓░▓',
                '▓░▓░▓▓',
                '▓░░▓▓▓',
                '▓░▓░▓▓',
                '▓░▓▓░▓',
                '▓▓▓▓▓▓'],
            'L': [

                '▓▓▓▓▓▓▓',
                '▓░░▓▓▓▓',
                '▓░░▓▓▓▓',
                '▓░░▓▓▓▓',
                '▓░░▓▓▓▓',
                '▓░░░░░▓',
                '▓▓▓▓▓▓▓'],
            'M': [

                '▓▓▓▓▓▓▓▓▓',
                '▓▓░▓▓▓░▓▓',
                '▓░▓░▓░▓░▓',
                '▓░▓▓░▓▓░▓',
                '▓░▓▓░▓▓░▓',
                '▓░▓▓░▓▓░▓',
                '▓▓▓▓▓▓▓▓▓'],
            'N': [

                '▓▓▓▓▓▓▓',
                '▓░▓▓▓░▓',
                '▓░░▓▓░▓',
                '▓░▓░▓░▓',
                '▓░▓▓░░▓',
                '▓░▓▓▓░▓',
                '▓▓▓▓▓▓▓'],

            'O': [

                '▓▓▓▓▓▓▓▓▓',
                '▓▓░░░░░▓▓',
                '▓░░▓▓▓░░▓',
                '▓░░▓▓▓░░▓',
                '▓░░▓▓▓░░▓',
                '▓▓░░░░░▓▓',
                '▓▓▓▓▓▓▓▓▓'],

            'P': [

                '▓▓▓▓▓▓▓',
                '▓░░░░▓▓',
                '▓░▓▓▓░▓',
                '▓░░░░▓▓',
                '▓░▓▓▓▓▓',
                '▓░▓▓▓▓▓',
                '▓▓▓▓▓▓▓'],
            'Q': [

                '▓▓▓▓▓▓▓▓▓▓▓▓',
                '▓▓▓░░░░░░▓▓▓',
                '▓▓░░▓▓▓▓░░▓▓',
                '▓▓░░▓▓▓▓░░▓▓',
                '▓▓░░▓▓▓░░░▓▓',
                '▓▓▓░░░░░░▓▓▓',
                '▓▓▓▓▓▓▓▓▓░▓▓'],
            'R': [

                '▓▓▓▓▓▓▓',
                '▓░░░░▓▓',
                '▓░▓▓▓░▓',
                '▓░░░░▓▓',
                '▓░▓▓▓░▓',
                '▓░▓▓▓░▓',
                '▓▓▓▓▓▓▓'],
            'S': [

                '▓▓▓▓▓▓▓',
                '▓▓░░░░▓',
                '▓░▓▓▓▓▓',
                '▓▓░░░▓▓',
                '▓▓▓▓▓░▓',
                '▓░░░░▓▓',
                '▓▓▓▓▓▓▓'],
            'T': [

                '▓▓▓▓▓▓▓',
                '▓░░░░░▓',
                '▓▓▓░▓▓▓',
                '▓▓▓░▓▓▓',
                '▓▓▓░▓▓▓',
                '▓▓▓░▓▓▓',
                '▓▓▓▓▓▓▓'],
            'U': [

                '▓▓▓▓▓▓▓',
                '▓░▓▓▓░▓',
                '▓░▓▓▓░▓',
                '▓░▓▓▓░▓',
                '▓░▓▓▓░▓',
                '▓▓░░░▓▓',
                '▓▓▓▓▓▓▓'],
            'V': [

                '▓▓▓▓▓▓▓▓▓',
                '▓░▓▓▓▓▓░▓',
                '▓░▓▓▓▓▓░▓',
                '▓▓░▓▓▓░▓▓',
                '▓▓▓░▓░▓▓▓',
                '▓▓▓▓░▓▓▓▓',
                '▓▓▓▓▓▓▓▓▓'],
            'W': [

                '▓▓▓▓▓▓▓▓▓',
                '▓░▓▓░▓▓░▓',
                '▓░▓▓░▓▓░▓',
                '▓░▓▓░▓▓░▓',
                '▓░▓░▓░▓░▓',
                '▓▓░▓▓▓░▓▓',
                '▓▓▓▓▓▓▓▓▓'],

            'X': [

                '▓▓▓▓▓▓▓',
                '▓░▓▓▓░▓',
                '▓▓░▓░▓▓',
                '▓▓▓░▓▓▓',
                '▓▓░▓░▓▓',
                '▓░▓▓▓░▓',
                '▓▓▓▓▓▓▓'],

            'Y': [

                '▓▓▓▓▓▓▓',
                '▓░▓▓▓░▓',
                '▓▓░▓░▓▓',
                '▓▓▓░▓▓▓',
                '▓▓▓░▓▓▓',
                '▓▓▓░▓▓▓',
                '▓▓▓▓▓▓▓'],

            'Z': [

                '▓▓▓▓▓▓▓',
                '▓░░░░░▓',
                '▓▓▓▓░░▓',
                '▓▓░░▓▓▓',
                '▓░▓▓▓▓▓',
                '▓░░░░░▓',
                '▓▓▓▓▓▓▓'],

            '.': [

                '▓▓▓▓',
                '▓▓▓▓',
                '▓▓▓▓',
                '▓▓▓▓',
                '▓▓▓▓',
                '▓░░▓',
                '▓▓▓▓'],

            ',': [

                '▓▓▓▓',
                '▓▓▓▓',
                '▓▓▓▓',
                '▓▓▓▓',
                '▓▓░▓',
                '▓░░▓',
                '▓▓▓▓'],
            "'": [

                '░░',
                '▓░',
                '▓▓',
                '▓▓',
                '▓▓',
                '▓▓',
                '▓▓'],

            "!": [

                '▓▓▓',
                '▓░▓',
                '▓░▓',
                '▓░▓',
                '▓▓▓',
                '▓░▓',
                '▓▓▓'],

            "?": [

                '▓▓▓▓▓▓',
                '▓░░░░▓',
                '▓▓▓▓░▓',
                '▓▓░░▓▓',
                '▓▓▓▓▓▓',
                '▓▓░░▓▓',
                '▓▓▓▓▓▓'],

            "~": [

                '▓▓▓▓▓▓▓▓▓▓▓▓▓▓',
                '▓▓▓▓▓▓▓▓▓▓▓▓▓▓',
                '▓▓▓░░░░▓▓▓▓░░▓',
                '▓▓░░▓▓░░▓▓░░▓▓',
                '▓░░▓▓▓▓░░░░▓▓▓',
                '▓▓▓▓▓▓▓▓▓▓▓▓▓▓',
                '▓▓▓▓▓▓▓▓▓▓▓▓▓▓'],

            "א": [

                '▓▓▓▓▓▓▓',
                '▓░▓▓▓░▓',
                '▓▓░▓▓░▓',
                '▓░▓░▓░▓',
                '▓░▓▓░▓▓',
                '▓░▓▓▓░▓',
                '▓▓▓▓▓▓▓'],

            "ב": [

                '▓▓▓▓▓▓▓',
                '▓░░░░▓▓',
                '▓▓▓▓░▓▓',
                '▓▓▓▓░▓▓',
                '▓▓▓▓░▓▓',
                '▓░░░░░▓',
                '▓▓▓▓▓▓▓'],

            "ג": [

                '▓▓▓▓▓▓▓',
                '▓░░░░▓▓',
                '▓▓▓▓░░▓',
                '▓▓▓▓░░▓',
                '▓▓░░░░▓',
                '▓░░▓░░▓',
                '▓▓▓▓▓▓▓'],

            "ד": [

                '▓▓▓▓▓▓▓',
                '▓░░░░░▓',
                '▓▓▓▓░▓▓',
                '▓▓▓▓░▓▓',
                '▓▓▓▓░▓▓',
                '▓▓▓▓░▓▓',
                '▓▓▓▓▓▓▓'],

            "ה": [

                '▓▓▓▓▓▓▓',
                '▓░░░░░▓',
                '▓▓▓▓▓░▓',
                '▓▓▓▓▓░▓',
                '▓▓░▓▓░▓',
                '▓▓░▓▓░▓',
                '▓▓▓▓▓▓▓'],

            "ו": [

                '▓▓▓▓',
                '▓░░▓',
                '▓░░▓',
                '▓░░▓',
                '▓░░▓',
                '▓░░▓',
                '▓▓▓▓'],

            "ז": [

                '▓▓▓▓▓▓▓',
                '▓░░░░░▓',
                '▓▓▓▓░▓▓',
                '▓▓▓░▓▓▓',
                '▓▓▓░▓▓▓',
                '▓▓▓░▓▓▓',
                '▓▓▓▓▓▓▓'],

            "ח": [

                '▓▓▓▓▓▓▓',
                '▓░░░░░▓',
                '▓░░░░░▓',
                '▓░▓▓▓░▓',
                '▓░▓▓▓░▓',
                '▓░▓▓▓░▓',
                '▓▓▓▓▓▓▓'],

            "ט": [

                '▓▓▓▓▓▓▓',
                '▓░▓▓▓░▓',
                '▓░▓▓░░▓',
                '▓░▓░▓░▓',
                '▓░▓▓▓░▓',
                '▓░░░░░▓',
                '▓▓▓▓▓▓▓'],

            "י": [

                '▓▓▓▓▓',
                '▓░░░▓',
                '▓▓▓░▓',
                '▓▓▓░▓',
                '▓▓▓▓▓',
                '▓▓▓▓▓',
                '▓▓▓▓▓'],

            "כ": [

                '▓▓▓▓▓▓▓',
                '▓░░░░░▓',
                '▓▓▓▓▓░▓',
                '▓▓▓▓▓░▓',
                '▓▓▓▓▓░▓',
                '▓░░░░░▓',
                '▓▓▓▓▓▓▓'],

            "ל": [

                '▓▓▓▓▓▓▓▓',
                '▓░▓▓▓▓▓▓',
                '▓░░░░░▓▓',
                '▓▓▓▓░░▓▓',
                '▓▓▓░░▓▓▓',
                '▓▓▓░▓▓▓▓',
                '▓▓▓▓▓▓▓▓'],

            "מ": [

                '▓▓▓▓▓▓▓',
                '▓░▓▓▓▓▓',
                '▓░░░░░▓',
                '▓░▓▓▓░▓',
                '▓░▓▓▓░▓',
                '▓░▓░░░▓',
                '▓▓▓▓▓▓▓'],

            "נ": [

                '▓▓▓▓▓▓▓',
                '▓▓▓░░░▓',
                '▓▓▓▓▓░▓',
                '▓▓▓▓▓░▓',
                '▓▓▓▓▓░▓',
                '▓░░░░░▓',
                '▓▓▓▓▓▓▓'],

            "ס": [

                '▓▓▓▓▓▓▓',
                '▓▓░░░▓▓',
                '▓░░▓░░▓',
                '▓░░▓░░▓',
                '▓░░▓░░▓',
                '▓▓░░░▓▓',
                '▓▓▓▓▓▓▓'],

            "ע": [

                '▓▓▓▓▓▓▓',
                '▓▓░▓▓░▓',
                '▓▓░▓▓░▓',
                '▓▓░▓▓░▓',
                '▓▓░▓▓░▓',
                '▓░░░░░▓',
                '▓▓▓▓▓▓▓'],

            "פ": [

                '▓▓▓▓▓▓▓',
                '▓░░░░░▓',
                '▓▓▓▓▓░▓',
                '▓░░░▓░▓',
                '▓░▓▓▓░▓',
                '▓░░░░░▓',
                '▓▓▓▓▓▓▓'],

            "צ": [

                '▓▓▓▓▓▓▓',
                '▓░▓▓▓░▓',
                '▓▓░▓░▓▓',
                '▓▓▓░▓▓▓',
                '▓▓▓▓░▓▓',
                '▓░░░░░▓',
                '▓▓▓▓▓▓▓'],

            "ק": [

                '▓▓▓▓▓▓▓',
                '▓░░░░░▓',
                '▓▓▓▓▓░▓',
                '▓▓░▓▓░▓',
                '▓▓░▓▓░▓',
                '▓▓░▓▓░▓',
                '▓▓░▓▓▓▓'],

            "ר": [

                '▓▓▓▓▓▓▓',
                '▓░░░░░▓',
                '▓▓▓▓▓░▓',
                '▓▓▓▓▓░▓',
                '▓▓▓▓▓░▓',
                '▓▓▓▓▓░▓',
                '▓▓▓▓▓▓▓'],

            "ש": [

                '▓▓▓▓▓▓▓',
                '▓░▓░▓░▓',
                '▓░▓░▓░▓',
                '▓░▓░▓░▓',
                '▓░▓░▓░▓',
                '▓░░░░░▓',
                '▓▓▓▓▓▓▓'],

            "ת": [

                '▓▓▓▓▓▓▓',
                '▓▓░░░░▓',
                '▓▓░▓▓░▓',
                '▓▓░▓▓░▓',
                '▓▓░▓▓░▓',
                '▓░░▓▓░▓',
                '▓▓▓▓▓▓▓'],

            "ץ": [

                '▓▓▓▓▓▓▓',
                '▓░▓▓▓░▓',
                '▓░▓▓▓░▓',
                '▓▓░▓░▓▓',
                '▓▓░░▓▓▓',
                '▓▓░▓▓▓▓',
                '▓▓░▓▓▓▓'],

            "ם": [

                '▓▓▓▓▓▓▓',
                '▓░░░░▓▓',
                '▓░▓▓▓░▓',
                '▓░▓▓▓░▓',
                '▓░▓▓▓░▓',
                '▓░░░░░▓',
                '▓▓▓▓▓▓▓'],

            "ן": [

                '▓▓▓▓▓',
                '▓░░░▓',
                '▓▓░░▓',
                '▓▓░░▓',
                '▓▓░░▓',
                '▓▓░░▓',
                '▓▓░░▓'],

            "ף": [

                '▓▓▓▓▓▓▓',
                '▓░░░░░▓',
                '▓░▓▓▓░▓',
                '▓░░▓▓░▓',
                '▓▓▓▓▓░▓',
                '▓▓▓▓▓░▓',
                '▓▓▓▓▓░▓'],

            "ך": [

                '▓▓▓▓▓▓▓',
                '▓░░░░░▓',
                '▓▓▓▓▓░▓',
                '▓▓▓▓▓░▓',
                '▓▓▓▓▓░▓',
                '▓▓▓▓▓░▓',
                '▓▓▓▓▓░▓']

        }

        numbers_list = []
        for num in string:
            try:
                numbers_list.append(numbers[num])
            except KeyError:
                raise commands.UserInputError

        output = ''
        for n in range(7):
            for i in range(len(numbers_list)):
                output += numbers_list[i][n]
            output += '\n'
        await ctx.send(output)

    @commands.command('bring-random', aliases=['br'])
    async def bring_random(self, ctx: commands.Context, channel: discord.VoiceChannel):
        permissions = ctx.author.permissions_in(channel)
        if permissions.move_members:
            member = random.choice(channel.members)
            await member.move_to(ctx.author.voice.channel)


def setup(bot):
    bot.add_cog(Fun(bot))
