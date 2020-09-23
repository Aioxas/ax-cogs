from redbot.core import commands
from redbot.cobot import Red
from redbot.coutils.chat_formatting import box

from random import choice
from aiohttp import ClientSession
from asyncio import sleep
from html import unescape
from re import findall, sub


class Geico(commands.Cog):
    """A 15-minute call could save you 15 percent (or more) on car insurance."""

    def __init__(self, bot: Red):
        self.bot = bot
        self.session = ClientSession(loop=self.bot.loop)

    def cog_unload(self):
        self.bot.loop.create_task(self.session.close())

    @commands.command(name="bash", pass_context=True, no_pm=True)
    @commands.cooldown(3, 60, commands.BucketType.user)
    async def _bash(self, ctx: commands.Context, num: int = 1) -> None:
        """Retrieves a quote from bash.org. num can be specified for number of quotes. Max is 5."""
        regex = [r"<p class=\"qt\">([^`]*?)<\/p>", r"<br \/>"]
        if num > 5:
            num = 5
            await ctx.send("Heck naw brah. 5 is max. Any more and you get killed.")
        i = 0
        while i < num:
            async with self.session.get("http://bash.org/?random") as resp:
                test = await resp.text()
                subs = findall(regex[0], test)
                brsub = sub(regex[1], "", subs[0])
                subs2 = unescape(brsub)
                await ctx.send(box(subs2))
                await sleep(1)
                i += 1

    @commands.command(name="quotes", pass_context=True, no_pm=True)
    @commands.cooldown(3, 60, commands.BucketType.user)
    async def _quotes(self, ctx: commands.Context, num: int, *, authors: str) -> None:
        """Retrieves a specified number of quotes from a specified author. Max number of quotes at a time is 5.
        Examples:
        [p]quotes 5 Morgan Freeman
        [p]quotes 2 Margaret Thatcher
        [p]quotes 5 Morgan Freeman; Margaret Thatcher"""
        regex = r"title=\"view quote\">([^`]*?)<\/a>"
        url = "http://www.brainyquote.com/quotes/authors/"
        author_list = authors.split(";")
        if num > 5:
            num = 5
            await ctx.send("Heck naw brah. 5 quotes per author is max. Any more and you get killed.")
        if len(author_list) > 5:
            author_list = author_list[:5]
            await ctx.send("Heck naw brah. 5 authors is max. Any more and you get killed.")
        try:
            for author in author_list:
                title = author[0].lower()
                url = (
                    url + title[0] + "/" + title.replace(" ", "_") + ".html"
                )
                async with self.session.get(url) as resp:
                    test = await resp.text()
                    quote_find = list(set(findall(regex, test)))
                if len(quote_find) == 0:
                    await ctx.send(f"Couldn't find any quotes for {author}. Moving on.")
                    continue
                i = 0
                while i < num:
                    random_quote = choice(quote_find)
                    quote_find.remove(random_quote)
                    while random_quote == title:
                        random_quote = choice(quote_find)
                    random_quote = (
                        random_quote.replace("&#39;", "'")
                        if "&#39;" in random_quote
                        else random_quote
                    )
                    await ctx.send(box(random_quote))
                    await sleep(1)
                    i += 1
        except IndexError:
            await ctx.send(
                "Your search is not valid, please follow the examples."
                "Make sure the names are correctly written\n"
                "[p]quotes 5 Margaret Thatcher\n[p]quotes 5 Morgan Freeman\n"
                "[p]quotes 5 Margaret Thatcher;Morgan Freeman"
            )
