import asyncio
from discord.ext import commands
import discord
import praw


class Reddit(commands.Cog):

    def __init__(self, bot: commands.bot):
        self.bot = bot
        self.reddit = praw.Reddit(client_id='LpZyJEaCETTdow',
                                  client_secret='CQt3JwPhuqyCkgvMHJClVxKIzbs',
                                  user_agent='ACoolBot')

    def cog_check(self, ctx: commands.Context):
        return ctx.channel.id in self.bot.get_data(ctx.guild.id, 'bot channels', [])

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
    @commands.bot_has_permissions(add_reactions=True, embed_links=True, read_message_history=True)
    async def hot(self,ctx: commands.Context, subreddit: str, limit:int = 20):
        sub = self.reddit.subreddit(subreddit).hot(limit=limit)
        embeds = self.sub2embeds(sub)
        if len(embeds) == 0:
            await ctx.send("No posts here, make sure you wrote the subreddit name right")
            return
        await asyncio.sleep(0.1)
        await self.bot.embeds_scroller(ctx, embeds)

    @commands.command()
    @commands.bot_has_permissions(add_reactions=True, embed_links=True, read_message_history=True)
    async def new(self,ctx: commands.Context, subreddit: str, limit: int = 20):
        sub = self.reddit.subreddit(subreddit).new(limit=limit)
        embeds = self.sub2embeds(sub)
        if len(embeds) == 0:
            await ctx.send("No posts here, make sure you wrote the subreddit name right")
            return
        await asyncio.sleep(0.1)
        await self.bot.embeds_scroller(ctx, embeds)


def setup(bot):
    bot.add_cog(Reddit(bot))
