from redbot.core import commands
from random import choice
from redbot.core.utils.chat_formatting import box
import aiohttp
import asyncio
import html
import re

from redbot.core.bot import Red

BaseCog = getattr(commands, "Cog", object)


class Geico(BaseCog):
    """A 15-minute call could save you 15 percent (or more) on car insurance."""

    def __init__(self, bot: Red):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=self.bot.loop)

    def __unload(self):
        self.session.close()

    @commands.command(name="bash", pass_context=True, no_pm=True)
    @commands.cooldown(3, 60, commands.BucketType.user)
    async def _bash(self, ctx, num: int = 1):
        """Retrieves a quote from bash.org. num can be specified for number of quotes. Max is 5."""
        regex = [r"<p class=\"qt\">([^`]*?)<\/p>", r"<br \/>"]
        if num > 5:
            num = 5
            await self.bot.reply("Heck naw brah. 5 is max. Any more and you get killed.")
        i = 0
        while i < num:
            async with self.session.get("http://bash.org/?random") as resp:
                test = str(await resp.text())
                subs = re.findall(regex[0], test)
                brsub = re.sub(regex[1], "", subs[0])
                subs2 = html.unescape(brsub)
                await ctx.send(box(subs2))
                await asyncio.sleep(1)
                i += 1

    @commands.command(name="quotes", pass_context=True, no_pm=True)
    @commands.cooldown(3, 60, commands.BucketType.user)
    async def _quotes(self, ctx, *, author: str):
        """Retrieves a specified number of quotes from a specified author. Max number of quotes at a time is 5.
        Examples:
        [p]quotes Morgan Freeman; 5
        [p]quotes Margaret Thatcher; 2"""
        regex = r"title=\"view quote\">([^`]*?)<\/a>"
        url = "http://www.brainyquote.com/quotes/authors/"
        try:
            author = author.split("; ")
            title = author[0]
            number = int(author[1])
            if number > 5:
                number = 5
                await self.bot.reply("Heck naw brah. 5 is max. Any more and you get killed.")
            url = url + title.lower()[0] + "/" + title.lower().replace(" ", "_") + ".html"
            async with self.session.get(url) as resp:
                test = str(await resp.text())
                quote_find = list(set(re.findall(regex, test)))
            i = 0
            while i < number:
                random_quote = choice(quote_find)
                quote_find.remove(random_quote)
                while random_quote == title:
                    random_quote = choice(quote_find)
                random_quote = (
                    random_quote.replace("&#39;", "'") if "&#39;" in random_quote else random_quote
                )
                await ctx.send(box(random_quote))
                await asyncio.sleep(1)
                i += 1

        except IndexError:
            await ctx.send(
                "Your search is not valid, please follow the examples."
                "Make sure the names are correctly written\n"
                "[p]quotes Margaret Thatcher; 5\n[p]quotes Morgan Freeman; 5"
            )


def setup(bot):
    n = Geico(bot)
    bot.add_cog(n)
