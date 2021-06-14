import json
import discord
from discord.ext import commands


def get_data(gid: int, name, default=None, data=None):
    if not data:
        data = json.load(open('data.json'))
    try:
        return data[str(gid)][name]
    except KeyError:
        set_data(gid, name, default)
        data = json.load(open('data.json'))
        return data[str(gid)][name]


def set_data(gid: int, name: str, val, data=None):
    if not data:
        data = json.load(open('data.json'))
    try:
        data[str(gid)].update({name: val})
    except KeyError:
        data.update({str(gid): {name: val}})
    json.dump(data, open('data.json', 'w'))


def owner_check():
    def predicate(ctx: commands.Context):
        return ctx.message.author.id == 254671305268264960
    return commands.check(predicate)


def moderation_check():
    def predicate(ctx: commands.Context):
        if ctx.guild:
            mod_role_id = get_data(ctx.guild.id, 'mod role', '')
            mod_role = discord.utils.find(lambda r: r.id == mod_role_id,
                                          ctx.guild.roles)
            if mod_role:
                return ctx.guild.roles.index(mod_role) <= ctx.guild.roles.index(ctx.author.top_role) or ctx.author.id == 254671305268264960
            else:
                return ctx.author.id == 254671305268264960 or ctx.author.guild_permissions.administrator == True

    return commands.check(predicate)


def higher_role_check():
    def predicate(ctx: commands.Context):
        if ctx.guild:
            return ctx.guild.roles.index(ctx.author.roles[-1]) > ctx.guild.roles.index(ctx.author.roles[-1]) or \
                   ctx.author.id == 254671305268264960
        return False

    return commands.check(predicate)


def in_bot_channel(ctx: commands.Context):
    if ctx.guild:
        return ctx.channel.id in get_data(ctx.guild.id, 'bot channels', [])
    return True
