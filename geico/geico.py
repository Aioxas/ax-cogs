import discord
import aiohttp
from discord.ext import commands
from .utils import checks
from __main__ import send_cmd_help
from random import choice
import re
from cogs.utils.chat_formatting import *
import html

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


    @commands.command(name="morgan",pass_context=True, no_pm=True)
    async def _morgan(self, ctx, num : int=1):
        """Retrieves a quote from bash.org. num can be specified for number of quotes. Max is 5."""
        if num > 5:
            num = 5
            await self.bot.reply("Heck naw brah. 5 is max. Any more and you get killed.")
        else:
            for i in range(num):
                async with aiohttp.get('http://www.brainyquote.com/quotes/authors/m/morgan_freeman.html') as resp:
                    test = await resp.content.read()
                    quote_find = self.morganregex.findall("{}".format(test))
                    random_quote = choice(quote_find)
                    while random_quote == 'Morgan Freeman':
                        random_quote = choice(quote_find)
                    single_quote_replace = self.morgan_single_quote_regex.sub("'", random_quote)        
                    await self.bot.say(box(single_quote_replace))
                            
    def bash_unescape(self, query):
        bash_unescape = html.unescape(query)
        break_sub = self.break_regex.sub("\n", bash_unescape)
        CR_LF_sub = self.CR_LF_removal_regex.sub("", break_sub)
        single_quote_sub = self.single_quote_regex.sub("'", CR_LF_sub)
        return single_quote_sub
        
def setup(bot):
    n = Geico(bot)
    bot.add_cog(n)
