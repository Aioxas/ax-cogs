from discord.ext import commands
from random import choice
from cogs.utils.chat_formatting import box
import aiohttp
import html
import re
import urllib


class Geico:
    """A 15-minute call could save you 15 percent (or more) on car insurance."""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="bash", pass_context=True, no_pm=True)
    @commands.cooldown(3, 60, commands.BucketType.user)
    async def _bash(self, ctx, num: int=1):
        """Retrieves a quote from bash.org. num can be specified for number of quotes. Max is 5."""
        regex = ["<p class=\"qt\">([^`]*?)<\/p>", "<br \/>"]
        if num > 5:
            num = 5
            await self.bot.reply("Heck naw brah. 5 is max. Any more and you get killed.")
        for i in range(num):
            async with aiohttp.request("GET", 'http://bash.org/?random') as resp:
                test = str(await resp.text())
                subs = re.findall(regex[0], test)
                brsub = re.sub(regex[1], "", subs[0])
                subs2 = html.unescape(brsub)
                await self.bot.say(box(subs2))

    @commands.command(name="quotes", pass_context=True, no_pm=True)
    @commands.cooldown(3, 60, commands.BucketType.user)
    async def _quotes(self, ctx, *, author: str):
        """Retrieves a specified number of quotes from a specified author. Max number of quotes at a time is 5.
        Examples:
        [p]quotes Morgan Freeman; 5
        [p]quotes Margaret Thatcher; 2"""
        regex = [" <a href=\"\/quotes\/authors\/([^`]*?).html\">", "title=\"view quote\">([^`]*?)<\/a>"]
        option = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'}
        try:
            author = author.split('; ')
            title = author[0]
            number = int(author[1])
            if number > 5:
                number = 5
                await self.bot.reply("Heck naw brah. 5 is max. Any more and you get killed.")
            uri = 'http://www.brainyquote.com/search_results.html?q='
            quary = title.lower()
            encode = urllib.parse.quote_plus(quary, encoding='utf-8', errors='replace')
            uir = uri + encode
            async with aiohttp.request("GET", uir, headers=option) as resp:
                test = str(await resp.text())
                author_find = re.findall(regex[0], test)
                author_url = 'http://www.brainyquote.com/quotes/authors/' + author_find[0]
                for i in range(number):
                    async with aiohttp.request("GET", author_url) as resp:
                        test = str(await resp.text())
                        quote_find = re.findall(regex[1], test)
                        random_quote = choice(quote_find)
                        while author in random_quote:
                            random_quote = choice(quote_find)
                        await self.bot.say(box(random_quote))

        except IndexError:
            await self.bot.say("Your search is not valid, please follow the examples."
                               "Make sure the names are correctly written\n"
                               "[p]quotes Margaret Thatcher; 5\n[p]quotes Morgan Freeman; 5")


def setup(bot):
    n = Geico(bot)
    bot.add_cog(n)
