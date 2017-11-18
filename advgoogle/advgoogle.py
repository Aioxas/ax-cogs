from discord.ext import commands
from random import choice
import aiohttp
import re
import urllib


class AdvancedGoogle:

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()
        
    def __unload(self):
        self.session.close()

    @commands.command(pass_context=True)
    @commands.cooldown(5, 60, commands.BucketType.server)
    async def google(self, ctx, text):
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
        result = await self.get_response(ctx)
        await self.bot.say(result)

    async def images(self, ctx, regex, option, images: bool=False):
        uri = "https://www.google.com/search?hl=en&tbm=isch&tbs=isz:m&q="
        num = 7
        if images:
            num = 8
        if isinstance(ctx, str):
            quary = str(ctx[num-1:].lower())
        else:
            quary = str(ctx.message.content
                        [len(ctx.prefix+ctx.command.name)+num:].lower())
        encode = urllib.parse.quote_plus(quary, encoding='utf-8',
                                         errors='replace')
        uir = uri+encode
        url = None
        async with self.session.get(uir, headers=option) as resp:
            test = await resp.content.read()
            unicoded = test.decode("unicode_escape")
            query_find = regex[0].findall(unicoded)
            try:
                if images:
                    url = choice(query_find)
                elif not images:
                    url = query_find[0]
                error = False
            except IndexError:
                error = True
        return url, error

    def parsed(self, find, regex, found: bool=True):
        find = find[:5]
        for r in find:
            if regex[3].search(r):
                m = regex[3].search(r)
                r = r[:m.start()] + r[m.end():]
            r = self.unescape(r)
        for i in range(len(find)):
            if i == 0:
                find[i] = "<" + find[i] + ">" + "\n\n**You might also want to check these out:**"
            else:
                find[i] = "<{}>".format(find[i])
        return find

    def unescape(self, msg):
        regex = ["<br \/>", "(?:\\\\[rn])", "(?:\\\\['])", "%25", "\(", "\)"]
        subs = ["\n", "", "'", "%", "%28", "%29"]
        for i in range(len(regex)):
            sub = re.sub(regex[i], subs[i], msg)
            msg = sub
        return msg

    async def get_response(self, ctx):
        if isinstance(ctx, str):
            search_type = ctx.lower().split(" ")
            search_valid = str(ctx.lower())
        else:
            search_type = ctx.message.content[len(ctx.prefix + ctx.command.name) + 1:].lower().split(" ")
            search_valid = str(ctx.message.content
                               [len(ctx.prefix + ctx.command.name) + 1:].lower())
        option = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'
        }
        regex = [
            re.compile(",\"ou\":\"([^`]*?)\""),
            re.compile("<h3 class=\"r\"><a href=\"\/url\?url=([^`]*?)&amp;"),
            re.compile("<h3 class=\"r\"><a href=\"([^`]*?)\""),
            re.compile("\/url?url=")
        ]

        # Start of Image
        if search_type[0] == "image" or search_type[0] == "images":
            msg = "Your search yielded no results."
            if search_valid == "image" or search_valid == "images":
                msg = "Please actually search something"
                return msg
            else:
                if search_type[0] == "image":
                    url, error = await self.images(ctx, regex, option)
                elif search_type[0] == "images":
                    url, error = await self.images(ctx, regex, option, images=True)
                if url and not error:
                    return url
                elif error:
                    return msg
                    # End of Image
        # Start of Maps
        elif search_type[0] == "maps":
            if search_valid == "maps":
                msg = "Please actually search something"
                return msg
            else:
                uri = "https://www.google.com/maps/search/"
                if isinstance(ctx, str):
                    quary = str(ctx[5:].lower())
                else:
                    quary = str(ctx.message.content
                                [len(ctx.prefix + ctx.command.name) + 6:].lower())
                encode = urllib.parse.quote_plus(quary, encoding='utf-8',
                                                 errors='replace')
                uir = uri + encode
                return uir
                # End of Maps
        # Start of generic search
        else:
            uri = "https://www.google.com/search?hl=en&q="
            if isinstance(ctx, str):
                quary = str(ctx)
            else:
                quary = str(ctx.message.content
                            [len(ctx.prefix + ctx.command.name) + 1:])
            encode = urllib.parse.quote_plus(quary, encoding='utf-8',
                                             errors='replace')
            uir = uri + encode
            async with self.session.get(uir, headers=option) as resp:
                test = str(await resp.content.read())
                query_find = regex[1].findall(test)
                if not query_find:
                    query_find = regex[2].findall(test)
                    try:
                        query_find = self.parsed(query_find, regex)
                    except IndexError:
                        return IndexError
                elif regex[3].search(query_find[0]):
                    query_find = self.parsed(query_find, regex)
                else:
                    query_find = self.parsed(query_find, regex, found=False)
            query_find = "\n".join(query_find)
            return query_find

            # End of generic search

    async def on_message(self, message):
        author = message.author

        if author == self.bot.user:
            return

        if not self.bot.user_allowed(message):
            return
        channel = message.channel
        str2find = "ok google "
        text = message.clean_content
        if not text.lower().startswith(str2find):
            return
        text = text.replace(str2find, "", 1)
        await self.bot.send_typing(channel)
        try:
            result = await self.get_response(text)
            await self.bot.send_message(channel, result)
        except IndexError:
            await self.bot.send_message(channel, "Your search yielded no results.")


def setup(bot):
    n = AdvancedGoogle(bot)
    bot.add_cog(n)
