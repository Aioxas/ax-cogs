from redbot.core import commands, checks
from redbot.core.bot import Red
from redbot.core.data_manager import cog_data_path
from redbot.core.utils.chat_formatting import inline

from aiohttp import ClientSession
from discord import File, Message
from glob import glob
from random import choice
from re import compile
from typing import List, Tuple
from urllib.parse import quote_plus, unquote
from os import remove, path, mkdir
from uuid import uuid4


class AdvancedGoogle(commands.Cog):
    def __init__(self, bot: Red):
        self.bot = bot
        self.session = ClientSession(loop=self.bot.loop)
        self.regex = [
            compile(r"style=\"border:1px solid #ccc;padding:1px\" src=\"([^`]*?)\""),
            compile(r"<div class=\"kCrYT\"><a href=\"/url?q=([^`]*?)&amp;sa=U"),
            compile(r"Please click <a href=\"([^`]*?)\">here</a>"),
            compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"),
        ]
        self.option = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            " AppleWebKit/537.36 (KHTML, like Gecko)"
            " Chrome/69.0.3497.100 Safari/537.36"
        }

    @checks.is_owner()
    @commands.command()
    async def googledebug(self, ctx: commands.Context, refID: str):
        """This command, given a refID
        will send html files to discord.
        This allows the cog creator to debug
        the issue with the proper html.
        Also purges those files from the advgoogle/debug folder"""
        fPath = str((cog_data_path(self) / "debug" / f"{refID}_*.html"))
        fileList = glob(fPath)
        if len(fileList) > 0:
            for filePath in fileList:
                await ctx.send(file=File(fp=filePath))
                remove(filePath)
            return
        await ctx.send("Please ensure that the refID provided is correct")

    @checks.is_owner()
    @commands.command()
    async def googledebugpurge(self, ctx: commands.Context):
        """This command purges the advgoogle/debug folder"""
        fPath = str((cog_data_path(self) / "debug" / "*.html"))
        fileList = glob(fPath)
        if len(fileList) > 0:
            for filePath in fileList:
                remove(filePath)
            return
        await ctx.send("No files to delete")

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(5, 60, commands.BucketType.channel)
    async def google(self, ctx: commands.Context, text: str):
        """Its google, you search with it.
        Example: google A magical pug

        Special search options are available; Image, Images, Maps
        Example: google image You know, for kids! > Returns first image
        Another example: google maps New York
        Another example: google images cats > Returns a random image
        based on the query

        Originally made by Kowlin https://github.com/Kowlin/Sentinel
        edited by Aioxas"""
        result, refID = await self.get_response(text)
        if result == "":
            await ctx.send(
                "No results returned."
                " Request the bot owner to run this command"
                " to get files to send to the cog creator"
                " for debugging: " + inline(f"{ctx.prefix}googledebug {refID}")
            )
            return
        fPath = str((cog_data_path(self) / "debug" / f"{refID}_*.html"))
        fileList = glob(fPath)
        if len(fileList) > 0:
            for filePath in fileList:
                remove(filePath)
        await ctx.send(result)

    async def images(self, text: str, images: bool = False):
        uri = "https://www.google.com/search?hl=en&tbm=isch&tbs=isz:m&q="
        quary = str(text.lower())
        uir = self.quote(uri, quary)
        async with self.session.get(uir, headers=self.option) as resp:
            test = await resp.content.read()
            unicoded = test.decode("unicode_escape")
            if len(result_find := self.regex[2].findall(unicoded)) > 0:
                async with self.session.get("https://www.google.com" + result_find[0].replace("&amp;", "&"), headers=self.option) as resp2:
                    test2 = await resp2.content.read()
                    unicoded = test2.decode("unicode_escape")
            query_find = self.regex[0].findall(unicoded)
            try:
                url = query_find[0]
                if images:
                    url = choice(query_find)
            except IndexError:
                error = True
            return url, error

    def parsed(self, find: List[str]) -> List[str]:
        find = find[:5] if len(find) > 5 else find
        for i, _ in enumerate(find):
            find[i] = f"<{self.unescape(find[i])}>"
            if i == 0:
                find[i] = find[i] + "\n\n**You might also want to check these out:**"
        return find

    def unescape(self, msg: str) -> str:
        msg = unquote(msg, encoding="utf-8", errors="replace")
        return msg

    def quote(self, uri: str, quary: str) -> str:
        encode = quote_plus(quary, encoding="utf-8", errors="replace")
        uir = uri + encode
        return uir

    async def get_response(self, text: str) -> Tuple[str, str]:
        search_query = str(text.lower()).split(" ")
        search_valid = search_query[0]
        quary = " ".join(search_query[1:]).lower()
        if len(search_query) == 1 and search_valid in ["images", "image", "maps"]:
            msg = "Please actually search something"
            return msg, ""
        elif search_valid in ["images", "image"]:  # Start of Image
            images = True if search_valid == "images" else False
            url, error = await self.images(text, images)
            if url and not error:
                return url, ""
            elif error:
                msg = "Your search yielded no results."
                return msg, ""  # End of Image
        elif search_valid == "maps":  # Start of Maps
            uri = "https://www.google.com/maps/search/"
            uir = self.quote(uri, quary)
            return uir, ""  # End of Maps
        else:  # Start of generic search
            uri = "https://www.google.com/search?hl=en&q="
            uir = self.quote(uri, quary)
            refID = str(uuid4())
            query_find = await self.result_returner(uir, refID, 0)
            if not ("\n" in query_find) and query_find != "":
                query_find = await self.result_returner(
                    uri + query_find.replace("&amp;", "&"), refID, 1
                )
            return query_find, refID  # End of generic search

    async def result_returner(self, uir: str, refID: str, attempt: int) -> str:
        debug_location = cog_data_path(self) / "debug"
        async with self.session.get(uir, headers=self.option) as resp:
            test = await resp.text()
            if not path.exists(str(debug_location)):
                mkdir(str(debug_location))
            with open(
                str(debug_location / f"{refID}_{attempt}.html"), "w", encoding="utf-8"
            ) as f:
                ip_find = self.regex[3].findall(test)
                for info in ip_find:
                    test.replace(info, "0.0.0.0")
                f.write(test)
            result_find = self.regex[1].findall(test)
            if (
                len(query_find := self.regex[2].findall(test)) == 1
                and len(result_find) == 0
            ):
                return query_find[0]
            try:
                result_find = "\n".join(self.parsed(result_find))
                return result_find
            except IndexError:
                return ""

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        ctx = await self.bot.get_context(message, cls=commands.Context)
        replacer_string = "ok "
        str2find = replacer_string + "google "
        text = message.clean_content.lower()
        if ctx.valid or not text.startswith(str2find):
            return
        prefix = ctx.prefix if isinstance(ctx.prefix, str) else ctx.prefix[0]
        message.content = message.content.replace(replacer_string, prefix)
        ctx.channel.typing()
        await self.bot.process_commands(message)

    def cog_unload(self):
        self.bot.loop.create_task(self.session.close())

    __unload = cog_unload
