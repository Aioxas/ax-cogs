from discord.ext import commands
from random import choice
import aiohttp
import re
import urllib


class AdvancedGoogle:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="advgoogle", pass_context=True, no_pm=True)
    @commands.cooldown(5, 60, commands.BucketType.user)
    async def _advgoogle(self, ctx, text):
        """Its google, you search with it.
        Example: google A magical pug

        Special search options are available; Image, Images, Maps
        Example: google image You know, for kids! > Returns first image
        Another example: google maps New York
        Another example: google images cats > Returns a random image
        based on the query
        LEGACY EDITION! SEE HERE!
        https://twentysix26.github.io/Red-Docs/red_cog_approved_repos/#refactored-cogs

        Originally made by Kowlin https://github.com/Kowlin/refactored-cogs
        edited by Aioxas"""
        search_type = ctx.message.content[len(ctx.prefix+ctx.command.name)+1:].lower().split(" ")
        option = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'
        }
        regex = [
            ",\"ou\":\"([^`]*?)\"",
            "<h3 class=\"r\"><a href=\"\/url\?url=([^`]*?)&amp;",
            "<h3 class=\"r\"><a href=\"([^`]*?)\""
            ]

        # Start of Image
        if search_type[0] == "image":
            search_valid = str(ctx.message.content
                               [len(ctx.prefix+ctx.command.name)+1:].lower())
            if search_valid == "image":
                await self.bot.say("Please actually search something")
            else:
                uri = "https://www.google.com/search?tbm=isch&tbs=isz:m&q="
                quary = str(ctx.message.content
                            [len(ctx.prefix+ctx.command.name)+7:].lower())
                encode = urllib.parse.quote_plus(quary, encoding='utf-8',
                                                 errors='replace')
                uir = uri+encode

                async with aiohttp.get(uir, headers=option) as resp:
                    test = await resp.content.read()
                    unicoded = test.decode("unicode_escape")
                    query_find = re.findall(regex[0], unicoded)
                    try:
                        url = query_find[0]
                        await self.bot.say(url)
                    except IndexError:
                        await self.bot.say("Your search yielded no results.")
            # End of Image
        # Start of Image random
        elif search_type[0] == "images":
            search_valid = str(ctx.message.content
                               [len(ctx.prefix+ctx.command.name)+1:].lower())
            if search_valid == "image":
                await self.bot.say("Please actually search something")
            else:
                uri = "https://www.google.com/search?tbm=isch&tbs=isz:m&q="
                quary = str(ctx.message.content
                            [len(ctx.prefix+ctx.command.name)+7:].lower())
                encode = urllib.parse.quote_plus(quary, encoding='utf-8',
                                                 errors='replace')
                uir = uri+encode
                async with aiohttp.get(uir, headers=option) as resp:
                    test = await resp.content.read()
                    unicoded = test.decode("unicode_escape")
                    query_find = re.findall(regex[0], unicoded)
                    try:
                        url = choice(query_find)
                        await self.bot.say(url)
                    except IndexError:
                        await self.bot.say("Your search yielded no results.")
            # End of Image random
        # Start of Maps
        elif search_type[0] == "maps":
            search_valid = str(ctx.message.content
                               [len(ctx.prefix+ctx.command.name)+1:].lower())
            if search_valid == "maps":
                await self.bot.say("Please actually search something")
            else:
                uri = "https://www.google.com/maps/search/"
                quary = str(ctx.message.content
                            [len(ctx.prefix+ctx.command.name)+6:].lower())
                encode = urllib.parse.quote_plus(quary, encoding='utf-8',
                                                 errors='replace')
                uir = uri+encode
                await self.bot.say(uir)
            # End of Maps
        # Start of generic search
        else:
            uri = "https://www.google.com/search?q="
            quary = str(ctx.message.content
                        [len(ctx.prefix+ctx.command.name)+1:])
            encode = urllib.parse.quote_plus(quary, encoding='utf-8',
                                             errors='replace')
            uir = uri+encode
            async with aiohttp.get(uir, headers=option) as resp:
                test = str(await resp.content.read())
                query_find = re.findall(regex[1], test)
                if not query_find:
                    query_find = re.findall(regex[2], test)
                    try:
                        if re.search("\/url?url=", query_find[0]):
                            query_find = query_find[0]
                            m = re.search("\/url?url=", query_find)
                            query_find = query_find[:m.start()]
                            + query_find[m.end():]
                            decode = self.unescape(query_find)
                            await self.bot.say("Here is your link: {}"
                                               .format(decode))
                        else:
                            decode = self.unescape(query_find[0])
                            await self.bot.say("Here is your link: {}"
                                               .format(decode))
                    except IndexError:
                        await self.bot.say("Your search yielded no results.")
                elif re.search("\/url?url=", query_find[0]):
                    query_find = query_find[0]
                    m = re.search("\/url?url=", query_find)
                    query_find = query_find[:m.start()] + query_find[m.end():]
                    decode = self.unescape(query_find)
                    await self.bot.say("Here is your link: {}".format(decode))
                else:
                    query_find = query_find[0]
                    decode = self.unescape(query_find)
                    await self.bot.say("Here is your link: {} ".format(decode))
            # End of generic search

    def unescape(self, msg):
        regex = ["<br \/>", "(?:\\\\[rn])", "(?:\\\\['])", "%25", "\(", "\)"]
        subs = ["\n", "", "'", "%", "%28", "%29"]

        for i in range(len(regex)):
            sub = re.sub(regex[i], subs[i], msg)
            msg = sub
        return msg


def setup(bot):
    n = AdvancedGoogle(bot)
    bot.add_cog(n)
