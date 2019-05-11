import random
from discord.ext import commands
from main import ACoolBot
import discord
import json
import datetime


def get_data(gid: int, name, default=None, data=json.load(open('data.json'))):
    try:
        return data[str(gid)][name]
    except KeyError:
        set_data(gid, name, default)
        return data[str(gid)][name]


def owner_check():
    def predicate(ctx: commands.Context):
        return ctx.message.author.id == 254671305268264960
    return commands.check(predicate)


def set_data(gid: int, name: str, val, data=json.load(open('data.json'))):
    try:
        data[str(gid)].update({name: val})
    except KeyError:
        data.update({str(gid): {name: val}})
    json.dump(data, open('data.json', 'w'))


def moderation_check():
    def predicate(ctx: commands.Context):
        if ctx.guild:
            mod_role = discord.utils.find(lambda r: r.id == get_data(ctx.guild.id, 'mod role'),
                                          ctx.guild.roles)
            if mod_role:
                return ctx.guild.roles.index(mod_role) <= ctx.guild.roles.index(ctx.author.top_role) or ctx.author.id == 254671305268264960
            else:
                return ctx.author.id == 254671305268264960
        else:
            return False

    return commands.check(predicate)


def higher_role_check():
    def predicate(ctx: commands.Context):
        if ctx.guild:
            return ctx.guild.roles.index(ctx.author.roles[-1]) > ctx.guild.roles.index(ctx.author.roles[-1]) or \
                   ctx.author.id == 254671305268264960
        return False

    return commands.check(predicate)


class Moderation(commands.Cog):

    def __init__(self, bot: ACoolBot):
        self.bot = bot

    async def cog_before_invoke(self, ctx: commands.Context):
        log_channel_id = ctx.bot.get_data(ctx.guild.id, 'bot log channel', None)
        if log_channel_id:
            log_channel = ctx.bot.get_channel(log_channel_id)
            if log_channel:
                embed = discord.Embed()
                embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
                embed.title = ctx.command.name
                embed.description = ctx.message.content
                embed.timestamp = datetime.datetime.now()
                try:
                    await log_channel.send(embed=embed)
                except Exception as e:
                    await self.bot.on_command_error(ctx, e)

    @commands.command(name='set-edit-channel', aliases=['sec','set_edit_channel'])
    @moderation_check()
    async def set_edit_channel(self, ctx: commands.context, channel: discord.TextChannel = None):
        if channel:
            self.bot.set_data(ctx.guild.id, "edit channel", channel.id)
            await ctx.send("Edit channel has been set to: "+channel.mention)
        else:
            self.bot.set_data(ctx.guild.id, "edit channel", channel)
            await ctx.send("I will no longer record edits, time to find a new thing to do with my spare time...")

    @commands.command(name='mod-role', aliases=['mr','mod_role'])
    @moderation_check()
    async def mod_role(self,ctx: commands.Context, role: discord.Role):
        self.bot.set_data(ctx.guild.id, 'mod role', role.id)
        await ctx.send('Mod role has been set to: {}'.format(role.name))

    @commands.command(name='set-delete-channel', aliases=['sdc','set_delete_channel'])
    @moderation_check()
    async def set_delete_channel(self, ctx: commands.Context, channel: discord.TextChannel = None):
        if channel:
            self.bot.set_data(ctx.guild.id, "delete channel", channel.id)
            await ctx.send("Deletion channel has been set to: " + channel.mention)
        else:
            self.bot.set_data(ctx.guild.id, "delete channel", channel)
            await ctx.send("I will no longer record deletions, time to find a new thing to do with my spare time...")

    @commands.command(name='set-log-channel', aliases=['slc','set_log_channel'])
    @moderation_check()
    async def set_log_channel(self, ctx: commands.Context, channel: discord.TextChannel = None):
        if channel:
            self.bot.set_data(ctx.guild.id, "bot log channel", channel.id)
            await ctx.send("bot log channel has been set to: " + channel.mention)
        else:
            self.bot.set_data(ctx.guild.id, "bot log channel", channel)
            await ctx.send("I will no longer record commands, time to find a new thing to do with my spare time...")

    @commands.command()
    @moderation_check()
    async def role_id(self, ctx: commands.Context, role: discord.Role):
        await ctx.send(role.id)

    @commands.command(name="admin-only")
    @moderation_check()
    async def admin_only(self, ctx: commands.Context, channel: discord.TextChannel = None):
        """
        set a channel so that only admins could write in
        :param commands.Context ctx:
        :param discord.TextChannel channel:
        :return:
        """
        if not channel:
            channel = ctx.channel
        channels = self.bot.get_data(ctx.guild.id, "admin only channels", [])
        if channel.id not in channels:
            channels.append(channel.id)
        else:
            channels.pop(channels.index(channel.id))
        self.bot.set_data(ctx.guild.id, "admin only channels", channels)
        await ctx.invoke(self.dont_log, channel)

    @commands.command(name="don't-log", aliases=('dont-log', 'dl'))
    @moderation_check()
    async def dont_log(self, ctx: commands.Context, channel: discord.TextChannel = None):
        if not channel:
            channel = ctx.channel
        unlogged_channels = self.bot.get_data(ctx.guild.id, "unlogged channels", [])
        if channel.id not in unlogged_channels:
            unlogged_channels.append(channel.id)
            await ctx.send("Channel: " + channel.mention + "has been added to `don't log`")
        else:
            unlogged_channels.pop(unlogged_channels.index(channel.id))
            await ctx.send("Channel: " + channel.mention + "has been removed from `don't log`")
        self.bot.set_data(ctx.guild.id, "unlogged channels", unlogged_channels)

    @commands.command(name='hotline', aliases=['hl'])
    @moderation_check()
    async def hotline(self, ctx: commands.Context, edgelord: discord.Member):
        embed = discord.Embed(title='Important Message')
        embed.description = "A server moderator has felt that you have been suicidal or has shown suicidal tendencies."\
                            " We care about you, and want to see you get better. Unfortunately, " \
                            "we are not qualified to do so. " \
                            "Please contact one of the numbers below if you feel like you want to end your life. " \
                            "Please don't end your life, it is precious to us.\n" \
                            "\n" \
                            "IF YOU ARE IN SERIOUS IMMEDIATE DANGER, " \
                            "PLEASE CONTACT 911 OR YOUR EMERGENCY SERVICE IN YOUR AREA."

        embed.add_field(name='**Suicide Hotlines:**',
                        value='https://en.wikipedia.org/wiki/List_of_suicide_crisis_lines')
        await edgelord.send(embed=embed)
        await ctx.send("successfully sent a hotline message to: " + edgelord.mention)

    @commands.command(name='warn')
    @moderation_check()
    @higher_role_check()
    async def warn(self, ctx: commands.Context, subject: discord.Member, *reason: str):
        pass

    @commands.command(name='ban')
    @moderation_check()
    @higher_role_check()
    async def ban(self, ctx: commands.Context, subject: discord.Member, *reason: str):
        reason = ' '.join(reason)
        await subject.ban(reason=reason)

    @commands.command(name='kick')
    @moderation_check()
    @higher_role_check()
    async def kick(self, ctx: commands.Context, subject: discord.Member, *reason: str):
        reason = ' '.join(reason)
        await subject.kick(reason=reason)

    @kick.after_invoke
    @ban.after_invoke
    @warn.after_invoke
    async def successfully(self, ctx: commands.Context):
        member = ctx.args[2]
        reason = ' '.join(ctx.args[3::])
        embed = discord.Embed(title=ctx.guild.name, color=int('0xFFFF00', 16))
        embed.description = "**Action by:** {ctx.author}\n" \
                            "**Action:** {ctx.command.name}\n" \
                            "**Reason:** {reason}".format(ctx=ctx, reason=reason)
        embed.timestamp = datetime.datetime.now()
        await member.send(embed=embed)
        await ctx.send("{member.mention} has been {ctx.command.name}ed".format(member=member, ctx=ctx))

    @commands.command(name='lock-channel', aliases=['lc'])
    @moderation_check()
    async def lock_channel(self, ctx: commands.Context, channels: commands.Greedy[discord.VoiceChannel]):
        for channel in channels:
            permissions = channel.overwrites_for(ctx.guild.default_role)
            if permissions.connect is None:
                permissions.connect = False
                await channel.set_permissions(ctx.guild.default_role, overwrite=permissions)
            else:
                permissions.connect = None
                await channel.set_permissions(ctx.guild.default_role, overwrite=permissions)

        await ctx.send("Command Completed Successfully")


def setup(bot):
    bot.add_cog(Moderation(bot))
