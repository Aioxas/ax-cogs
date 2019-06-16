from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.data_manager import cog_data_path
from redbot.core.utils.chat_formatting import inline
from random import choice
import aiohttp
import asyncio
import discord
import glob
import os
import re
import urllib
import uuid

BaseCog = getattr(commands, "Cog", object)


class AdvancedGoogle(BaseCog):
    def __init__(self, bot: Red):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=self.bot.loop)
        self.regex = [
            re.compile(r",\"ou\":\"([^`]*?)\""),
            re.compile(r"class=\"r\"><a href=\"([^`]*?)\""),
            re.compile(r"Please click <a href=\"([^`]*?)\">here<\/a>"),
        ]
        self.option = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
        }

    def __unload(self):
        self.bot.loop.create_task(self.session.close())

    @commands.command()
    async def googledebug(self, ctx, refID):
        """This command, given a refID
        will send html files to discord.
        This allows the cog creator to debug
        the issue with the proper html"""
        fPath = str((cog_data_path(self) / "debug" / f"{refID}_*.html"))
        fileList = glob.glob(fPath)
        if len(fileList) > 0:
            for filePath in fileList:
                await ctx.send(file=discord.File(fp=filePath))
        else:
            await ctx.send("Please ensure that the refID provided is correct")

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(5, 60, commands.BucketType.channel)
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
        result, refID = await self.get_response(ctx)
        if refID != "" and result == "":
            await ctx.send(f" No results returned. Run this command to get files to" + 
                            f"send to the cog creator for further debugging:" +
                             inline(f"{ctx.prefix}googledebug {refID}"))
        else:
            fPath = str((cog_data_path(self) / "debug" / f"{refID}_*.html"))
            fileList = glob.glob(fPath)
            if len(fileList) > 0:
                for filePath in fileList:
                    os.remove(filePath)
            await ctx.send(result)

    async def images(self, ctx, images: bool = False):
        uri = "https://www.google.com/search?hl=en&tbm=isch&tbs=isz:m&q="
        num = 7
        if images:
            num = 8
        if isinstance(ctx, str):
            quary = str(ctx[(num - 1):].lower())
        else:
            quary = str(ctx.message.content[(len(ctx.prefix + ctx.command.name) + num):].lower())
        encode = urllib.parse.quote_plus(quary, encoding="utf-8", errors="replace")
        uir = uri + encode
        url = None
        async with self.session.get(uir, headers=self.option) as resp:
            test = await resp.content.read()
            unicoded = test.decode("unicode_escape")
            query_find = self.regex[0].findall(unicoded)
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
        if len(find) > 5:
            find = find[:5]
        for i, _ in enumerate(find):
            if i == 0:
                find[i] = "<{}>\n\n**You might also want to check these out:**".format(
                    self.unescape(find[i])
                )
            else:
                find[i] = "<{}>".format(self.unescape(find[i]))
        return find

    def unescape(self, msg):
        msg = urllib.parse.unquote_plus(msg, encoding="utf-8", errors="replace")
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
                ctx.message.content[(len(ctx.prefix + ctx.command.name) + 1):].lower()
            )

        # Start of Image
        if search_type[0] == "image" or search_type[0] == "images":
            msg = "Your search yielded no results."
            if search_valid == "image" or search_valid == "images":
                msg = "Please actually search something"
                return msg, ""
            else:
                if search_type[0] == "image":
                    url, error = await self.images(ctx)
                elif search_type[0] == "images":
                    url, error = await self.images(ctx, images=True)
                if url and not error:
                    return url, ""
                elif error:
                    return msg, ""
                    # End of Image
        # Start of Maps
        elif search_type[0] == "maps":
            if search_valid == "maps":
                msg = "Please actually search something"
                return msg, ""
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
                return uir, ""
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
            refID = uuid.uuid4()
            query_find = await self.result_returner(uir, refID, "0")
            if isinstance(query_find, str):
                query_find = await self.result_returner(
                    url + query_find.replace("&amp;", "&"),
                    refID,
                    "1"
                )
            query_find = "\n".join(query_find)
            return query_find, refID
            # End of generic search

    async def result_returner(self, uir, refID, attempt):
        async with self.session.get(uir, headers=self.option) as resp:
            test = await resp.text()
            with open(str(cog_data_path(self) / "debug" / f"{refID}_{attempt}.html"), "w") as f:
                f.write(test)
            query_find = self.regex[2].findall(test)
            result_find = self.regex[1].findall(test)
            if len(query_find) == 1 and len(result_find) == 0:
                return query_find[0]
            try:
                result_find = self.parsed(result_find)
            except IndexError:
                return IndexError
        return result_find

    @commands.Cog.listener()
    async def on_message(self, message):
        ctx = await self.bot.get_context(message, cls=commands.Context)
        str2find = "ok google "
        text = message.clean_content.lower()
        if ctx.valid or not text.startswith(str2find):
            return
        if ctx.guild is None:
            ctx.prefix = await ctx.bot.db.prefix()
        else:
            ctx.prefix = await ctx.bot.db.guild(ctx.guild).prefix()
            if len(ctx.prefix) == 0:
                ctx.prefix = await ctx.bot.db.prefix()
        message.content = message.content.replace(str2find, ctx.prefix[0] + "google ")
        ctx.channel.typing()
        await self.bot.process_commands(message)
