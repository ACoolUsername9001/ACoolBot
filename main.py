#!venv/bin/python
import traceback
from discord.ext import commands
import discord
from discord import utils
import datetime
import time
import json


def owner_check():
    def predicate(ctx: commands.Context):
        return ctx.message.author.id == 254671305268264960

    return commands.check(predicate)


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

        for extension in self.all_cogs:
            self.load_extension(extension)
        # self.add_command(self.invite)
        self.data = json.load(open('data.json'))
        self.add_command(self.reload_cogs)
        self.add_command(self.invite)

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
        else:
            before_role = utils.find(lambda r: r.name == before.channel.name, before.channel.guild.roles)
        roles = member.roles

        if before.channel is not None:
            if before_role in roles:
                await member.remove_roles(before_role, reason='voice connectivity')

        if after.channel is not None:
            if after_role not in roles:
                await member.add_roles(after_role, reason='Voice connectivity')

    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState,
                                    after: discord.VoiceState):
        if before.channel is not None:
            if before.channel.category.name is not 'TEMP VOICE':
                await self.give_role_voice_channel(member, before, after)
        else:
            await self.give_role_voice_channel(member, before, after)
        if member.guild.afk_channel and after.channel is not None and after.channel is not member.guild.afk_channel and\
                member.id in self.get_data(member.guild.id, "afk purgatory", []):
            await member.move_to(member.guild.afk_channel)
        # await self.create_channel_type(member, before, after)

    async def create_channel_type(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):

        if before.channel is not None:
            if len(before.channel.members) is 0:
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
            if not message.author.bot and message.channel.id not in self.get_data(message.guild.id,
                                                                                  "unlogged channels", []):
                if self.get_data(message.guild.id, "delete channel"):
                    channel = discord.utils.find(lambda c: c.id == self.get_data(message.guild.id, "delete channel"),
                                                 message.guild.channels)
                    description = '**User:** {} `[{}]`\n**Channel:** {} `[{}]`\n{}'.format(message.author.mention,
                                                                                           message.author.name,
                                                                                           message.channel.mention,
                                                                                           message.channel.name,
                                                                                           message.content)
                    embed = discord.Embed(title='Deleted Message', color=int('0xFF0000', 16), description=description,
                                          type='rich')
                    if message.attachments:
                        embed.add_field(name='**Attachments:** ', value='\n'.join(message.attachments.proxy_url))
                    embed.set_footer(text='Message ID: ' + str(message.id))
                    embed.timestamp = message.created_at
                    await channel.send(embed=embed)

    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.guild:
            if not before.author.bot and before.channel.id not in self.get_data(before.guild.id,
                                                                                "unlogged channels", []):
                if self.get_data(before.guild.id, "edit channel"):
                    channel = discord.utils.find(lambda c: c.id == self.get_data(before.guild.id, "edit channel"),
                                                 before.guild.channels)
                    description = '**User:** {} `[{}]`\n**Channel:** {} `[{}]`'.format(before.author.mention,
                                                                                       before.author.name,
                                                                                       before.channel.mention,
                                                                                       before.channel.name)
                    embed = discord.Embed(title='Edited Message', color=int('0x00FF00', 16), description=description,
                                          type='rich')
                    embed.add_field(name='**before**', value=before.content)
                    if before.attachments:
                        embed.add_field(name='**Attachments:** ', value='\n'.join(before.attachments))
                    embed.add_field(name='**after**', value=after.content)
                    if after.attachments:
                        embed.add_field(name='**Attachments:** ', value='\n'.join(after.attachments))
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
    def is_admin(author: discord.Member):
        return author.guild_permissions.administrator and not author.bot


if __name__ == '__main__':
    bot = ACoolBot()
    key = json.load(open('DiscordKey.json'))
    bot.run(key["key"])
