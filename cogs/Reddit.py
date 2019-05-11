import asyncio
from discord.ext import commands
import discord
import praw


class Reddit(commands.Cog):

    def __init__(self, bot: commands.bot):
        self.bot = bot
        self.pages = {}
        self.reddit = praw.Reddit(client_id = 'LpZyJEaCETTdow',
                                client_secret='CQt3JwPhuqyCkgvMHJClVxKIzbs',
                                user_agent='ACoolBot')

    async def embeds_scroller(self,ctx:commands.Context, embeds):
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
                reaction, user = await self.bot.wait_for('reaction_add', check=scroll, timeout=120.0)
                if user is not self.bot:
                    await message.remove_reaction(reaction, user)
                if user is ctx.author:
                    try:
                        try:
                            await message.edit(embed=embeds[self.pages[message.id]])
                        except IndexError:
                            self.pages.update({message.id: 0})
                            await message.edit(embed=embeds[self.pages[message.id]])
                    except:
                        self.pages.update({message.id: self.pages[message.id] + 1})
                        try:
                            await message.edit(embed=embeds[self.pages[message.id]])
                        except IndexError:
                            self.pages.update({message.id: 0})
                            await message.edit(embed=embeds[self.pages[message.id]])

            except asyncio.TimeoutError:
                await message.remove_reaction('▶', self.bot.user)
                await message.remove_reaction('◀', self.bot.user)
                break
        return

    @staticmethod
    def sub2embeds(sub):
        embeds = []
        for post in sub:
            if not post.stickied:
                title = post.title
                if len(title) > 256:
                    title = title[0:252] + '...'
                embed = discord.Embed(title=title, url='http://www.reddit.com' + post.permalink)
                if (not post.selftext == '') and post.selftext:
                    description = []
                    text = post.selftext
                    lines = text.split('\n')
                    block = ''
                    for line in lines:
                        if len(line) > 1024:
                            for l in line.split(' '):
                                if len(block + l + ' ') > 1024 or l == '&#x200B;':
                                    if block.strip() is not '':
                                        description.append(block)
                                    block = ''
                                if not l == '&#x200B;':
                                    block += l + ' '
                            continue
                        if len(block + line + '\n') > 1024 or line == '&#x200B;':
                            if block.strip() is not '':
                                description.append(block)
                            block = ''
                        if not line == '&#x200B;' or line == '':
                            block += line + '\n'
                    if block.strip() is not '':
                        description.append(block)
                    for d in description:
                        if d.strip() is not '':
                            embed.add_field(name='-', value=d)
                if hasattr(post, 'preview'):
                    try:
                        embed.set_image(url=post.preview['images'][0]['variants']['gif']['source']['url'])
                    except KeyError:
                        embed.set_image(url=post.preview['images'][0]['source']['url'])
                embeds.append(embed)
        return embeds

    @commands.command()
    @commands.bot_has_permissions(add_reactions=True, embed_links=True,
                         read_message_history=True)
    async def hot(self,ctx: commands.Context, subreddit: str, limit:int = 20):
        sub = self.reddit.subreddit(subreddit).hot(limit=limit)
        embeds = self.sub2embeds(sub)
        if len(embeds) == 0:
            await ctx.send("No posts here, make sure you wrote the subreddit name right")
            return
        await asyncio.sleep(0.1)
        await self.embeds_scroller(ctx, embeds)

    @commands.command()
    @commands.bot_has_permissions(add_reactions=True, embed_links=True,
                                  read_message_history=True)
    async def new(self,ctx: commands.Context, subreddit: str, limit: int = 20):
        sub = self.reddit.subreddit(subreddit).new(limit=limit)
        embeds = self.sub2embeds(sub)
        if len(embeds) == 0:
            await ctx.send("No posts here, make sure you wrote the subreddit name right")
            return
        await asyncio.sleep(0.1)
        await self.embeds_scroller(ctx,embeds)


def setup(bot):
    bot.add_cog(Reddit(bot))
