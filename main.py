#!venv/bin/python
import traceback
from discord.ext import commands
import discord
from discord import utils
import datetime
import time
import json
import asyncio

from discord.ext.commands import DefaultHelpCommand

from cogs.checks import owner_check, in_bot_channel


def join_attachment_urls(attachments: [discord.Attachment]):
    return '\n'.join(map(lambda a: a.url, attachments))


class ACoolBot(commands.Bot):

    def __init__(self, **options):

        super().__init__(self.command_prefix, **options)
        self.member_converter = commands.MemberConverter()
        self.all_cogs = [
            'cogs.Fun',
            'cogs.Moderation',
            'cogs.Reddit',
            'cogs.Abuse'
        ]
        self.pages = {}
        for extension in self.all_cogs:
            self.load_extension(extension)
        self.data = json.load(open('data.json'))
        self.add_command(self.reload_cogs)
        self.add_command(self.invite)
        self.add_command(self.give_role)
        self.add_command(self.leave)
        self.help_command.add_check(in_bot_channel)

    def command_prefix(self, bot, message: discord.Message):
        if not message.guild:
            return '*'
        prefixes = self.get_data(message.guild.id, 'prefix', ['*'])
        return commands.when_mentioned_or(*prefixes)(self, message)

    def set_data(self, gid: int, name: str, val):
        try:
            self.data[str(gid)].update({name: val})
        except KeyError:
            self.data.update({str(gid): {name: val}})
        json.dump(self.data, open('data.json', 'w'))

    def get_data(self, gid: int, name, default=None):
        try:
            return self.data[str(gid)][name]
        except KeyError:
            self.set_data(gid, name, default)
            return self.data[str(gid)][name]

    async def on_ready(self):
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,
                                                             name="humanity withering away"))

    @staticmethod
    async def give_role_voice_channel(member: discord.Member, before: discord.VoiceState,
                                      after: discord.VoiceState):
        if before.channel == after.channel:
            return

        if after.channel is not None:
            if before.channel is not None:
                before_role = utils.find(lambda r: r.name.lower() == before.channel.name.lower(), member.guild.roles)
            after_role = utils.find(lambda r: r.name.lower() == after.channel.name.lower(), member.guild.roles)
            if after_role is None:
                after_role = utils.find(lambda r: r.name.lower() == after.channel.name.lower(),
                                        after.channel.guild.roles)
            if after_role is None:
                after_role = await after.channel.guild.create_role(name=after.channel.name)

        roles = member.roles

        if before.channel is not None:
            before_role = utils.find(lambda r: r.name == before.channel.name, roles)
            if before_role in roles:
                await member.remove_roles(before_role, reason='voice connectivity')

        if after.channel is not None:
            if after_role not in roles:
                await member.add_roles(after_role, reason='Voice connectivity')

    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState,
                                    after: discord.VoiceState):
        await self.give_role_voice_channel(member, before, after)
        # await self.create_channel_type(member, before, after)

    async def create_channel_type(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):

        if before.channel is not None:
            if len(before.channel.members) == 0:
                type = before.channel.name.strip(' I')
                voice_channels = list(filter(lambda c: type == c.name.strip(' I') and len(c.members) == 0,
                                             member.guild.channels.copy()))
                text_channel = list(filter(lambda c: type.lower().replace(' ', "-") == c.name.strip(' i'),
                                           member.guild.channels.copy()))
                if len(voice_channels) > 1:
                    await voice_channels[0].delete()
                    if len(text_channel) > 1:
                        await text_channel[0].delete()
                    role = discord.utils.find(lambda r: r.name == voice_channels[-1].name, member.guild.roles.copy())
                    if role is not None:
                        await role.delete()

        if after.channel is not None:
            type = after.channel.name.strip(' I')
            voice_channels = list(filter(lambda c: type == c.name.strip(' I') and len(c.members) == 0,
                                         member.guild.channels.copy()))
            text_channel = list(filter(lambda c: type.lower().replace(' ', "-") == c.name.strip(' i'),
                                       member.guild.channels.copy()))
            if len(voice_channels) == 0:
                guild = member.guild
                name = type + ' ' + 'I' * (len(list(filter(lambda c: type == c.name.strip(' I'),
                                                           member.guild.channels.copy()))) + 1)

                try:
                    def_role_name = self.get_data(guild.id, 'default role')
                except KeyError:
                    self.set_data(guild.id, 'default role', 'Member')
                    def_role_name = self.get_data(guild.id, 'default role')
                def_role = utils.find(lambda r: r.name == def_role_name, guild.roles.copy())
                if def_role is None:
                    def_role = await guild.create_role(name=def_role_name)

                role = await guild.create_role(name=name, color=discord.Color(int('303136', 16)))

                overwrites_text = {
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    role: discord.PermissionOverwrite(read_messages=True)
                }
                overwrites_voice = {
                    guild.default_role: discord.PermissionOverwrite(connect=False),
                    def_role: discord.PermissionOverwrite(connect=True)
                }
                await guild.create_voice_channel(name=name, category=after.channel.category,
                                                 overwrites=overwrites_voice)
                await guild.create_text_channel(name=name.lower().replace(' ', '-'), category=text_channel[0].category,
                                                overwrites=overwrites_text)

    @staticmethod
    async def on_guild_channel_update(before, after):
        if type(before) is discord.VoiceChannel:
            if before.name is not after.name:
                role = discord.utils.find(lambda r: r.name == before.name, before.guild.roles)
                await role.edit(name=after.name)

    @staticmethod
    async def on_guild_channel_delete(before):
        if type(before) is discord.VoiceChannel:
            role = discord.utils.find(lambda r: r.name == before.name, before.guild.roles)
            await role.delete()

    async def on_command_error(self, ctx: commands.Context, error):
        ignored = commands.CommandNotFound
        error = getattr(error, 'original', error)

        if isinstance(error, ignored):
            return

        if hasattr(ctx.command, 'on_error'):
            return

        elif isinstance(error, commands.DisabledCommand):
            return
        elif isinstance(error, commands.CheckFailure):
            return
        elif isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.author.send('{} can not be used in Private Messages.'.format(ctx.command))
            except:
                pass
        elif isinstance(error, commands.errors.CommandOnCooldown):
            return await ctx.send(error)
        elif isinstance(error, commands.UserInputError):
            return await ctx.send('Invalid input')
        try:

            embed = discord.Embed(title='**__Error on command "' + ctx.command.name + '":__**',
                                  description=str(error)[-1024:],
                                  timestamp=datetime.datetime.fromtimestamp(time.time()),
                                  color=990000, type="rich")
        except IndexError:
            embed = discord.Embed(title='**__Error on command "' + ctx.command.name + '":__**',
                                  description=str(error)[:1024], timestamp=datetime.datetime.fromtimestamp(time.time()),
                                  color=990000, type="rich")
        try:
            embed.add_field(name="**Type**", value=str(type(error))[-1024:], inline=False)
        except IndexError:
            embed.add_field(name="**Type**", value=str(type(error))[:1024], inline=False)

        try:
            embed.add_field(name='**Author**', value=ctx.message.author.nick, inline=False)
        except AttributeError:
            embed.add_field(name='**Author**', value=ctx.message.author.name, inline=False)

        embed.add_field(name="**Full command:**", value=ctx.message.content, inline=False)
        if not isinstance(ctx.message.channel, discord.DMChannel):
            embed.add_field(name='**Channel**', value='<#' + str(ctx.message.channel.id) + '> `[' +
                            ctx.message.channel.name + ']`', inline=False)
        if ctx.guild:
            embed.add_field(name='**Guild**', value=ctx.guild.name, inline=False)
        else:
            embed.add_field(name='**Guild**', value='Private Message', inline=False)
        trace = traceback.format_exception(type(error), error, error.__traceback__, chain=False)
        try:
            embed.add_field(name="**Traceback:**", value=''.join(trace)[-1024:], inline=False)
        except IndexError:
            embed.add_field(name="**Traceback:**", value=''.join(trace)[:1024], inline=False)
        members = self.get_all_members()
        member = discord.utils.find(lambda m: m.id == 254671305268264960, members)
        return await member.send(content='', embed=embed)

    async def on_message_delete(self, message: discord.Message):
        if message.guild:
            if message.channel.id not in self.get_data(message.guild.id, "unlogged channels", []):
                if self.get_data(message.guild.id, "delete channel"):
                    if not message.content:
                        return

                    channel = discord.utils.find(lambda c: c.id == self.get_data(message.guild.id, "delete channel"),
                                                 message.guild.channels)
                    description = '**User:** {} `[{}]`\n**Channel:** {} `[{}]`\n{}'.format(message.author.mention,
                                                                                           message.author.name,
                                                                                           message.channel.mention,
                                                                                           message.channel.name,
                                                                                           message.content if message.content else 'ACoolBot failed to get message data')
                    embed = discord.Embed(title='Deleted Message', color=int('0xFF0000', 16), description=description,
                                          type='rich')
                    if message.attachments:
                        embed.add_field(name='**Attachments:** ', value='\n'.join((a.proxy_url for a in message.attachments)))
                    embed.set_footer(text='Message ID: ' + str(message.id))
                    embed.timestamp = message.created_at
                    await channel.send(embed=embed)

    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.guild:
            if before.channel.id not in self.get_data(before.guild.id, "unlogged channels", []):
                if self.get_data(before.guild.id, "edit channel"):
                    if before.content == after.content and join_attachment_urls(before.attachments) == join_attachment_urls(after.attachments):
                        return
                    channel = discord.utils.find(lambda c: c.id == self.get_data(before.guild.id, "edit channel"),
                                                 before.guild.channels)
                    description = '**User:** {} `[{}]`\n**Channel:** {} `[{}]`'.format(before.author.mention,
                                                                                       before.author.name,
                                                                                       before.channel.mention,
                                                                                       before.channel.name)
                    embed = discord.Embed(title='Edited Message', color=int('0x00FF00', 16), description=description,
                                          type='rich')
                    if before.content:
                        embed.add_field(name='**before**', value=before.content, inline=False)

                    if after.content:
                        embed.add_field(name='**after**', value=after.content, inline=False)

                    if before.attachments:
                        embed.add_field(name='**Before Attachments:** ', value=join_attachment_urls(before.attachments), inline=False)

                    if after.attachments:
                        embed.add_field(name='**After Attachments:** ', value=join_attachment_urls(after.attachments), inline=False)

                    embed.set_footer(text='Message ID: ' + str(after.id))
                    if after.edited_at:
                        embed.timestamp = after.edited_at
                    await channel.send(embed=embed)

    @staticmethod
    @commands.command(name='reload-cogs', aliases=['rc', 'reload'])
    @owner_check()
    async def reload_cogs(ctx):
        for cog in ctx.bot.all_cogs:
            try:
                ctx.bot.unload_extension(cog)
            except commands.ExtensionNotLoaded:
                pass
            ctx.bot.load_extension(cog)
        await ctx.send('Done!')

    async def on_message(self, message: discord.Message):
        if not message.author == self.user:
            await self.process_commands(message)
        if message.guild:
            admin_only_channels = self.get_data(message.guild.id, "admin only channels", [])
            watchlist_log = self.get_data(message.guild.id, 'watchlist-log', None)
            watchlist = [w[0] for w in self.get_data(message.guild.id, 'watchlist', [])]
            watchlist_log = discord.utils.find(lambda c: c.id == watchlist_log, message.guild.text_channels)
            if watchlist_log:
                if message.author.id in watchlist and not message.author.bot:
                    description = '**User:** {} `[{}]`\n**Channel:** {} `[{}]`\n{}'.format(message.author.mention,
                                                                                           message.author.name,
                                                                                           message.channel.mention,
                                                                                           message.channel.name,
                                                                                           message.content)
                    embed = discord.Embed(title='Watchlist Message', color=int('0xFF00FF', 16), description=description,
                                          type='rich')
                    if message.attachments:
                        embed.add_field(name='**Attachments:** ', value='\n'.join([a.proxy_url
                                                                                   for a in message.attachments]))
                    embed.set_footer(text='Message ID: ' + str(message.id))
                    embed.timestamp = message.created_at
                    await watchlist_log.send(embed=embed)

            if admin_only_channels:
                if message.channel.id in admin_only_channels and not self.is_admin(message.author):
                    await message.delete()

    @staticmethod
    @commands.command(name='invite')
    @owner_check()
    async def invite(ctx: commands.Context):
        await ctx.send(
            'https://discordapp.com/oauth2/authorize?&client_id={}&scope=bot&permissions=8'.format(ctx.bot.user.id))

    @staticmethod
    @commands.command(name='leave')
    @owner_check()
    async def leave(ctx: commands.Context):
        await ctx.guild.leave()

    @staticmethod
    def is_admin(author: discord.Member):
        return author.guild_permissions.administrator and not author.bot

    async def embeds_scroller(self, ctx: commands.Context, embeds):
        embeds[0].set_footer(text='page: 1/{}'.format(len(embeds)))
        message = await ctx.send(embed=embeds[0])
        await message.add_reaction('◀')
        await asyncio.sleep(0.1)
        await message.add_reaction('▶')
        self.pages.update({message.id: 0})

        def scroll(reaction: discord.Reaction, user: discord.User):
            if reaction.message.id == message.id and not user.bot:
                if user == ctx.author and str(reaction.emoji) == '◀':
                    self.pages.update({reaction.message.id: self.pages[reaction.message.id] - 1})
                elif user == ctx.author and str(reaction.emoji) == '▶':
                    self.pages.update({reaction.message.id: self.pages[reaction.message.id] + 1})
                return True
            else:
                return False

        while True:
            try:
                reaction, user = await self.wait_for('reaction_add', check=scroll, timeout=120.0)
                if user is not self:
                    await message.remove_reaction(reaction, user)

                if user == ctx.author:
                    index = self.pages[message.id] % len(embeds)
                    embeds[index].set_footer(text='page: {page}/{total}'.format(page=self.pages[message.id]
                                                                                % len(embeds) + 1,
                                                                                total=len(embeds)))
                    await message.edit(embed=embeds[index])

            except asyncio.TimeoutError:
                await message.remove_reaction('▶', self.user)
                await message.remove_reaction('◀', self.user)
                break
        return
    
    def is_banned_word(self, message: discord.Message):
        """
        checks whether a banned word is in a message
        :param message: discord message object
        return bool: True if banned word is found else False
        """
        banned_words_list = self.get_data(message.guild.id, 'banned words', [])
        for banned_word in banned_words_list:
            if banned_word in message.content:
                return True
        return False

    @staticmethod
    @commands.command('pyramid', hidden=True)
    async def give_role(ctx):
        if ctx.guild and ctx.guild.id == 530154962777407509:
            rules_role = ctx.guild.get_role(542308860937895949)
            await ctx.author.add_roles(rules_role, reason='give_role command')


if __name__ == '__main__':
    intents = discord.Intents.default()
    intents.typing = False
    intents.presences = False
    intents.bans = False
    intents.members = True

    bot = ACoolBot(intents=intents, max_messages=10000, owner_id=254671305268264960)
    key = json.load(open('DiscordKey.json'))
    bot.run(key["key"])
