import discord
import aiohttp
from discord.ext import commands
from .utils import checks
from __main__ import send_cmd_help
from random import choice
import re
from cogs.utils.chat_formatting import *
import html
import urllib

class Geico:
    """A 15-minute call could save you 15 percent (or more) on car insurance."""
    def __init__(self, bot):
        self.bot = bot
        self.bashregex = re.compile("<p class=\"qt\">([^`]*?)<\/p>")
        self.break_regex = re.compile("<br \/>")
        self.CR_LF_removal_regex = re.compile("(?:\\\\[rn])")
        self.single_quote_regex = re.compile("(?:\\\\['])")
        self.morganregex = re.compile("title=\"view quote\">([^`]*?)<\/a>")
        self.morgan_single_quote_regex = re.compile("&#39;")
        self.quoteregex = re.compile(" <a href=\"\/quotes\/authors\/([^`]*?).html\">")
        self.option = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'}

    @commands.command(name="bash", pass_context=True, no_pm=True)
    async def _bash(self, ctx, num : int=1):
        """Retrieves a quote from bash.org. num can be specified for number of quotes. Max is 5."""
        if num > 5:
            num = 5
            await self.bot.reply("Heck naw brah. 5 is max. Any more and you get killed.")
        else:
            for i in range(num):
                async with aiohttp.get('http://bash.org/?random') as resp:
                    test = await resp.content.read()
                    quote_find = self.bashregex.findall("{}".format(test))
                    blank_space_replace = self.bash_unescape(quote_find[0])
                    await self.bot.say(box(blank_space_replace))

    @commands.command(name="quotes",pass_context=True, no_pm=True)
    async def _quotes(self, ctx, *, author : str):
        """Retrieves a specified number of quotes from a specified author. Max number of quotes at a time is 5.
           Example:
           [p]quotes Morgan Freeman; 5
           [p]quotes Margaret Thatcher; 2"""
        try:
            author = author.split('; ')
            title = author[0]
            number = int(author[1])
            if number > 5:
                number = 5
                await self.bot.reply("Heck naw brah. 5 is max. Any more and you get killed.")
                uri = 'http://www.brainyquote.com/search_results.html?q='
                quary = str(title).lower()
                encode = urllib.parse.quote_plus(quary,encoding='utf-8',errors='replace')
                uir = uri + encode
                async with aiohttp.get(uir, headers = self.option) as resp:
                    test = await resp.content.read()
                    author_find = self.quoteregex.findall("{}".format(test))
                    author_url = 'http://www.brainyquote.com/quotes/authors/' + str(author_find[0])
                    for i in range(number):
                        async with aiohttp.get(author_url) as resp:
                            test = await resp.content.read()
                            quote_find = self.morganregex.findall("{}".format(test))
                            random_quote = choice(quote_find)
                            nameregex = re.compile("<h1 class=\"pull-left quoteListH1\" style=\"padding-right:20px\">([^`]*?) Quotes")
                            name_find = nameregex.findall("{}".format(test))
                            name = str(name_find[0])
                            while random_quote == name:
                                random_quote = choice(quote_find)
                            single_quote_replace = self.morgan_single_quote_regex.sub("'", random_quote)
                            await self.bot.say(box(single_quote_replace))
            else:
                uri = 'http://www.brainyquote.com/search_results.html?q='
                quary = str(title).lower()
                encode = urllib.parse.quote_plus(quary,encoding='utf-8',errors='replace')
                uir = uri + encode
                async with aiohttp.get(uir, headers = self.option) as resp:
                    test = await resp.content.read()
                    author_find = self.quoteregex.findall("{}".format(test))
                    author_url = 'http://www.brainyquote.com/quotes/authors/' + str(author_find[0])
                    for i in range(number):
                        async with aiohttp.get(author_url) as resp:
                            test = await resp.content.read()
                            quote_find = self.morganregex.findall("{}".format(test))
                            random_quote = choice(quote_find)
                            nameregex = re.compile("<h1 class=\"pull-left quoteListH1\" style=\"padding-right:20px\">([^`]*?) Quotes")
                            name_find = nameregex.findall("{}".format(test))
                            name = str(name_find[0])
                            while random_quote == name:
                                random_quote = choice(quote_find)
                            single_quote_replace = self.morgan_single_quote_regex.sub("'", random_quote)
                            await self.bot.say(box(single_quote_replace))

        except IndexError:
            await self.bot.say("Your search is not valid, please follow the examples.\n[p]quotes Margaret Thatcher; 5\n[p]quotes Morgan Freeman; 5")
                            
def bash_unescape(self, query):
        bash_unescape = html.unescape(query)
        break_sub = self.break_regex.sub("\n", bash_unescape)
        CR_LF_sub = self.CR_LF_removal_regex.sub("", break_sub)
        single_quote_sub = self.single_quote_regex.sub("'", CR_LF_sub)
        return single_quote_sub
        
def setup(bot):
    n = Geico(bot)
    bot.add_cog(n)
