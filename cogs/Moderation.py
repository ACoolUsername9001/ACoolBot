from discord.ext import commands

from cogs.checks import moderation_check, higher_role_check
from main import ACoolBot
import discord
import datetime


class Moderation(commands.Cog):

    def __init__(self, bot: ACoolBot):
        self.bot = bot

    async def cog_before_invoke(self, ctx: commands.Context):
        log_channel_id = ctx.bot.get_data(ctx.guild.id, 'bot log channel', None)
        if log_channel_id:
            log_channel = ctx.bot.get_channel(log_channel_id)
            if log_channel:
                embed = discord.Embed()
                embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar)
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
            if channel.id not in self.bot.get_data(ctx.guild.id, 'unlogged channels', []):
                await ctx.invoke(self.dont_log, channel)
        else:
            channels.pop(channels.index(channel.id))
            if channel.id in self.bot.get_data(ctx.guild.id, 'unlogged channels', []):
                await ctx.invoke(self.dont_log, channel)
        self.bot.set_data(ctx.guild.id, "admin only channels", channels)

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
    
    @commands.command(name="watchlist-add")
    @moderation_check()
    async def watchlist_add(self, ctx: commands.Context, member: discord.Member, *reason: str):
        watchlist = self.bot.get_data(ctx.guild.id, "watchlist", [])
        reason = " ".join(reason)

        if watchlist:
            watchlisted_members = [x[0] for x in watchlist]
            if member.id in watchlisted_members:
                await ctx.send("{} already on watchlist".format(member.mention))
                return

        if reason == '':
            await ctx.send('You must specify a reason for being on a watchlist')
            return

        watchlist.append((member.id, reason))
        self.bot.set_data(ctx.guild.id, "watchlist", watchlist)
        await ctx.send("added {member} to watchlist".format(member=member.mention))

    @commands.command(name="watchlist-remove")
    @moderation_check()
    async def watchlist_remove(self, ctx: commands.Context, member: discord.Member):
        watchlist = self.bot.get_data(ctx.guild.id, "watchlist", [])
        if watchlist:
            for i in range(len(watchlist)):
                if watchlist[i][0] == member.id:
                    watchlist.remove(watchlist[i])
                    await ctx.send("removed {member} from the watchlist".format(member=member.mention))
                    return
            await ctx.send("{} was not found in watchlist".format(member.mention))
        else:
            await ctx.send("watchlist is empty")

    @commands.command(name="watchlist-clear")
    @moderation_check()
    async def watchlist_clear(self, ctx: commands.Context):
        self.bot.set_data(ctx.guild.id, "watchlist", [])
        await ctx.send("cleared the watchlist, it is empty now")

    @commands.command(name='watchlist-log')
    @moderation_check()
    async def watchlist_log(self, ctx: commands.Context, channel: discord.TextChannel = None):
        if not channel:
            self.bot.set_data(ctx.guild.id, 'watchlist-log', None)
            await ctx.send("watchlist will not be logged")
            return
        await ctx.send("watchlist will be logged in <#{channel.id}>".format(channel=channel))
        self.bot.set_data(ctx.guild.id, 'watchlist-log', channel.id)

    @commands.command(name='watchlist-view')
    @moderation_check()
    async def watchlist_view(self, ctx: commands.Context):
        watchlist = self.bot.get_data(ctx.guild.id, 'watchlist', [])
        member_converter = commands.MemberConverter()
        embeds = []
        watchlist_data = watchlist.copy()
        for i in range(len(watchlist)):
            try:
                await member_converter.convert(ctx, str(watchlist[i][0]))
            except commands.BadArgument:
                watchlist_data.remove(watchlist[i])
        self.bot.set_data(ctx.guild.id, 'watchlist', watchlist_data)

        for i in range(len(watchlist)//5 + 1):
            embed = discord.Embed(title='watchlist', color=0xFF00FF)
            for member_id, reason in watchlist_data[i*5:(i+1)*5]:
                member = await member_converter.convert(ctx, str(member_id))
                embed.add_field(name='{member.name} ({member.id})'.format(member=member),
                                value=reason if reason != '' else '*no reason was specified*', inline=False)
            embeds.append(embed)
        for embed in embeds.copy():
            if not len(embed.fields):
                embeds.remove(embed)
        await self.bot.embeds_scroller(ctx, embeds)

    @commands.command(name='autoban-add')
    @moderation_check()
    async def autoban_add(self, ctx: commands.Context, member_id):
        autoban_list = self.bot.get_data(ctx.guild.id, 'autoban list', [])
        if member_id in autoban_list:
            await ctx.send("this member is already in the autoban list")
            return
        autoban_list.append(member_id)
        self.bot.set_data(ctx.guild.id, 'autoban list', autoban_list)
        await ctx.send('member added to auto ban list')

    @commands.command(name='autoban-remove')
    @moderation_check()        
    async def autoban_remove(self, ctx: commands.Context, member_id):
        autoban_list = self.bot.get_data(ctx.guild.id, 'autoban list', [])
        if member_id in autoban_list:
            autoban_list.pop(autoban_list.index(member_id))
            return await ctx.send('member was removed from the list')
        return await ctx.send('member was not found in the autoban list')

    @commands.command(name='bot-channel-add')
    @moderation_check()
    async def add_bot_channel(self, ctx: commands.Context, channels: commands.Greedy[discord.TextChannel]):
        bot_channels = self.bot.get_data(ctx.guild.id, 'bot channels', [])
        bot_channels.extend([c.id for c in channels])
        bot_channels = list(set(bot_channels))
        self.bot.set_data(ctx.guild.id, 'bot channels', bot_channels)
        await ctx.send('added channels: {} from bot channels'.format(', '.join([c.mention for c in channels])))

    @commands.command(name='bot-channel-remove')
    @moderation_check()
    async def remove_bot_channel(self, ctx: commands.Context, channels: commands.Greedy[discord.TextChannel]):
        bot_channels = self.bot.get_data(ctx.guild.id, 'bot channels', [])
        for channel in channels:
            if channel.id in bot_channels:
                bot_channels.remove(channel.id)
        self.bot.set_data(ctx.guild.id, 'bot channels', bot_channels)
        await ctx.send('removed channels: {} from bot channels'.format(', '.join([c.mention for c in channels])))

    @commands.command(name='bot-channel-view')
    @moderation_check()
    async def view_bot_channel(self, ctx: commands.Context):
        bot_channels = self.bot.get_data(ctx.guild.id, 'bot channels', [])
        await ctx.send('active bot channels: {}'.format(', '.join(['<#{}>'.format(c) for c in bot_channels])))


async def setup(bot):
    await bot.add_cog(Moderation(bot))
