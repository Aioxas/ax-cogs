from discord.ext import commands
from random import choice
import aiohttp
import re
import urllib


class AdvancedGoogle:
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()
        self.option = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
        }
        self.regex = [
            re.compile(',"ou":"([^`]*?)"'),
            re.compile('<h3 class="r"><a href="\/url\?q=([^`]*?)&amp;'),
            re.compile('<h3 class="r"><a href="([^`]*?)"'),
            re.compile("\/url?q="),
            re.compile(r"<a href=\"([^`]*?)\">here<\/a>"),
        ]

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

    async def images(self, ctx, regex, images: bool = False):
        uri = "https://www.google.com/search?hl=en&tbm=isch&tbs=isz:m&q="
        num = 7
        if images:
            num = 8
        if isinstance(ctx, str):
            quary = str(ctx[num - 1 :].lower())
        else:
            quary = str(
                ctx.message.content[len(ctx.prefix + ctx.command.name) + num :].lower()
            )
        encode = urllib.parse.quote_plus(quary, encoding="utf-8", errors="replace")
        uir = uri + encode
        url = None
        async with self.session.get(uir, headers=self.option) as resp:
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

    def parsed(self, find):
        find = find[:5]
        for i, r in enumerate(find):
            if self.regex[3].search(r):
                m = self.regex[3].search(r)
                find[i] = r[: m.start()] + r[m.end() :]
            if i == 0:
                find[i] = "<{}>\n\n**You might also want to check these out:**".format(
                    self.unescape(find[i])
                )
            else:
                find[i] = "<{}>".format(self.unescape(find[i]))
        return find

    def unescape(self, msg):
        msg = urllib.parse.unquote_plus(msg, encoding="utf-8", errors="replace")
        regex = [r"<br \/>", r"(?:\\\\[rn])", r"(?:\\\\['])", r"%25", r"\(", r"\)"]
        subs = [r"\n", r"", r"'", r"%", r"%28", r"%29"]
        for i, reg in enumerate(regex):
            sub = re.sub(reg, subs[i], msg)
            msg = sub
        return msg

    async def get_response(self, ctx):
        if isinstance(ctx, str):
            search_type = ctx.lower().split(" ")
            search_valid = str(ctx.lower())
        else:
            search_type = (
                ctx.message.content[len(ctx.prefix + ctx.command.name) + 1 :]
                .lower()
                .split(" ")
            )
            search_valid = str(
                ctx.message.content[len(ctx.prefix + ctx.command.name) + 1 :].lower()
            )

        # Start of Image
        if search_type[0] == "image" or search_type[0] == "images":
            msg = "Your search yielded no results."
            if search_valid == "image" or search_valid == "images":
                msg = "Please actually search something"
                return msg
            else:
                if search_type[0] == "image":
                    url, error = await self.images(ctx, regex)
                elif search_type[0] == "images":
                    url, error = await self.images(ctx, regex, images=True)
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
                    quary = str(
                        ctx.message.content[
                            len(ctx.prefix + ctx.command.name) + 6 :
                        ].lower()
                    )
                encode = urllib.parse.quote_plus(
                    quary, encoding="utf-8", errors="replace"
                )
                uir = uri + encode
                return uir
                # End of Maps
        # Start of generic search
        else:
            url = "https://www.google.com"
            uri = url + "/search?hl=en&q="
            if isinstance(ctx, str):
                quary = str(ctx)
            else:
                quary = str(
                    ctx.message.content[len(ctx.prefix + ctx.command.name) + 1 :]
                )
            encode = urllib.parse.quote_plus(quary, encoding="utf-8", errors="replace")
            uir = uri + encode
            query_find = await self.result_returner(uir)
            if isinstance(query_find, str):
                query_find = await self.result_returner(
                    url + query_find.replace("&amp;", "&")
                )
            query_find = "\n".join(query_find)
            return query_find
            # End of generic search

    async def result_returner(self, uir):
        async with self.session.get(uir, headers=self.option) as resp:
            test = str(await resp.content.read())
            query_find = self.regex[4].findall(test)
            if len(query_find) == 1:
                return query_find[0]

            query_find = self.regex[1].findall(test)
            try:
                query_find = self.parsed(query_find)
            except IndexError:
                query_find = self.regex[2].findall(test)
                try:
                    query_find = self.parsed(query_find)
                except IndexError:
                    return IndexError
        return query_find

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
