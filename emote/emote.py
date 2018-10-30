import aiohttp
import itertools
import asyncio
import discord
import os
import re

from PIL import Image
from redbot.core import Config, checks, commands
from redbot.core.bot import Red
from redbot.core.data_manager import cog_data_path
# if this seem hard to read/understand, remove the comments. Might make it easier

BaseCog = getattr(commands, "Cog", object)


class Emote(BaseCog):
    """Emote was made using irdumb's sadface cog's code.

    Owner is responsible for it's handling."""

    default_guild_settings = {"status": False, "emotes": {}}

    def __init__(self, bot: Red):
        self.bot = bot
        self._emote = Config.get_conf(self, 1824791591)
        self._emote_path = cog_data_path(self) / "images"

        self._emote.register_guild(**self.default_guild_settings)

        self.session = aiohttp.ClientSession(loop=self.bot.loop)

    # doesn't make sense to use this command in a pm, because pms aren't in servers
    # mod_or_permissions needs something in it otherwise it's mod or True which is always True

    def __unload(self):
        self.session.close()

    @commands.group()
    @commands.guild_only()
    async def emotes(self, ctx):
        """Emote settings"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help()

    @emotes.command()
    @checks.mod_or_permissions(manage_roles=True)
    @commands.guild_only()
    async def set(self, ctx):
        """Enables/Disables emotes for this server"""
        # default off.
        guild = ctx.guild
        status = not await self._emote.guild(guild).status()
        await self._emote.guild(guild).status.set(status)
        # for a toggle, settings should save here in case bot fails to send message
        if status:
            await ctx.send(
                "Emotes on. Please turn this off in the Red - DiscordBot server."
                " This is only an example cog."
            )
        else:
            await ctx.send("Emotes off.")

    @emotes.command()
    @checks.is_owner()
    @commands.guild_only()
    async def add(self, ctx, name, url):
        """Allows you to add emotes to the emote list
        [p]emotes add pan http://i.imgur.com/FFRjKBW.gifv"""
        guild = ctx.guild
        name = name.lower()
        emotes = await self._emote.guild(guild).emotes()
        option = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36"
        }
        if not url.endswith((".gif", ".gifv", ".png")):
            await ctx.send(
                "Links ending in .gif, .png, and .gifv are the only ones accepted."
                "Please try again with a valid emote link, thanks."
            )
            return
        if name in emotes:
            await ctx.send("This keyword already exists, please use another keyword.")
            return
        if url.endswith(".gifv"):
            url = url.replace(".gifv", ".gif")
        try:
            await ctx.send("Downloading {}.".format(name))
            async with self.session.get(url, headers=option) as r:
                emote = await r.read()
                print(self._emote_path)
                with open(self._emote_path + "{}.{}".format(name, url[-3:]), "wb") as f:
                    f.write(emote)

                await ctx.send("Adding {} to the list.".format(name))
                emotes[name] = "{}.{}".format(name, url[-3:])
                await self._emote.guild(guild).emote.set(emotes)
            await ctx.send("{} has been added to the list".format(name))
        except Exception as e:
            print(e)
            await ctx.send(
                "It seems your url is not valid,"
                " please make sure you are not typing names with spaces as they are and then the url."
                " If so, do [p]emotes add name_with_spaces url"
            )

    @checks.is_owner()
    @emotes.command()
    @commands.guild_only()
    async def remove(self, ctx, name):
        """Allows you to remove emotes from the emotes list"""
        guild = ctx.guild
        name = name.lower()
        emotes = await self._emote.guild(guild).emotes()
        try:
            if name in emotes:
                os.remove(self._emote + emotes[name])
                del emotes[name]
            else:
                await ctx.send(
                    "{} is not a valid name, please make sure the name of the"
                    " emote that you want to remove actually exists."
                    " Use [p]emotes list to verify it's there.".format(name)
                )
                return
            await self._emote.guild(guild).emote.set(emotes)
            await ctx.send("{} has been removed from the list".format(name))
        except FileNotFoundError:
            await ctx.send(
                "For some unknown reason, your emote is not available in the default directory"
                ", that is, data/emote/images. This means that it can't be removed. "
                "But it has been successfully removed from the emotes list."
            )

    @checks.is_owner()
    @emotes.command()
    @commands.guild_only()
    async def edit(self, ctx, name, newname):
        """Allows you to edit the keyword that triggers the emote
         from the emotes list"""
        guild = ctx.guild
        name = name.lower()
        emotes = await self._emote.guild(guild).emotes()
        if newname in emotes:
            await ctx.send("This keyword already exists, please use another keyword.")
            return
        try:
            if name in emotes:
                emotes[newname] = "{}.{}".format(newname, emotes[name][-3:])
                os.rename(self._emote + emotes[name], self._emote + emotes[newname])
                del emotes[name]
            else:
                await ctx.send(
                    "{} is not a valid name, please make sure the name of the"
                    " emote that you want to edit exists"
                    " Use [p]emotes list to verify it's there.".format(name)
                )
                return
            await self._emote.guild(guild).emote.set(emotes)
            await ctx.send("{} in the emotes list has been renamed to {}".format(name, newname))
        except FileNotFoundError:
            await ctx.send(
                "For some unknown reason, your emote is not available in the default directory,"
                " that is, data/emote/images. This means that it can't be edited."
                " But it has been successfully edited in the emotes list."
            )

    @emotes.command()
    @commands.guild_only()
    async def list(self, ctx, style):
        """Shows you the emotes list.
        Supported styles: [p]emotes list 10 (shows 10 emotes per page)
        and [p]emotes list a (shows all the emotes beginning with a)"""
        guild = ctx.guild
        style = style.lower()
        emotes = await self._emote.guild(guild).emotes()
        istyles = sorted(emotes)
        if not istyles:
            await ctx.send(
                "Your emotes list is empty."
                " Please add a few emotes using the [p]emote add function."
            )
            return
        if style.isdigit():
            if style == "0":
                await ctx.send("Only numbers from 1 to infinite are accepted.")
                return
            style = int(style)
            istyle = istyles
        elif style.isalpha():
            istyle = []
            for i in range(len(istyles)):
                ist = re.findall("\\b" + style + "\\w+", istyles[i])
                istyle = istyle + ist
            style = 10
        else:
            await ctx.send(
                "Your list style is not correct, please use one"
                " of the accepted styles, either do [p]emotes list A or [p]emotes list 10"
            )
            return
        s = "\n"
        count = style
        counter = len(istyle) + count
        while style <= counter:
            if style <= count:
                y = s.join(istyle[:style])
                await ctx.send("List of available emotes:\n{}".format(y))
                if style > len(istyle):
                    return
                style += count
            elif style > count:
                style2 = style - count
                y = s.join(istyle[style2:style])
                await ctx.send("Continuation:\n{}".format(y))
                if style > len(istyle):
                    return
                style += count
            await ctx.send("Do you want to continue seeing the list? Yes/No")

            def check(m):
                return m.content.lower().strip() in ["yes", "no"] and m.author == ctx.author

            try:
                answer = await self.bot.wait_for("messsage", timeout=15, check=check)
            except asyncio.TimeoutError:
                return
            else:
                if answer.content.lower().strip() == "yes":
                    continue
                return

    @checks.is_owner()
    @emotes.command()
    @commands.guild_only()
    async def compare(self, ctx, style, alls: str = None):
        """Allows you to compare keywords to files
        or files to keywords and then make sure that
        they all coincide.
        Keywords to Files name: K2F
        Files to Keywords name: F2K
        [p]emotes compare K2F
        [p]emotes compare K2F all
        [p]emotes compare F2K all"""
        guild = ctx.guild
        style = style.lower()
        if alls is not None:
            alls = alls.lower()
        styleset = ["k2f", "f2k"]
        if style not in styleset:
            return
        msg = "Keywords deleted due to missing files in the emotes list:\n"
        c = list()
        for entry in os.scandir(str(self._emote_path)):
            c.append(entry.name)
        if style == styleset[0]:
            if alls == "all":
                servers = sorted(await self._emote.guilds())
                servers.remove("emote")
                for servs in servers:
                    missing = list()
                    server = await self._emote.guild(servs).emotes()
                    istyles = sorted(server)
                    for n in istyles:
                        cat = "|".join(c)
                        if not n[0].isalnum():
                            z = re.compile(r"\B" + n + r"\b")
                        else:
                            z = re.compile(r"\b" + n + r"\b")
                        if z.search(cat) is None:
                            missing.append(n)
                    if not missing:
                        await ctx.send("All files and keywords are accounted for in " + servs)
                        if len(servers) == servers.index(servs):
                            return
                        else:
                            continue
                    for m in missing:
                        if m in server:
                            del server[m]
                    await self._emote.guild(servs).emote.set(server)
                    s = "\n"
                    style = 10
                    counter = len(missing) + 10
                    while style <= counter:
                        if style <= 10:
                            y = s.join(missing[:style])
                            await ctx.send(msg + y)
                            if style >= len(missing):
                                break
                            style += 10
                        elif style > 10:
                            style2 = style - 10
                            y = s.join(missing[style2:style])
                            await ctx.send("Continuation:\n{}".format(y))
                            if style >= len(missing):
                                break
                            style += 10
                        await ctx.send("Do you want to continue seeing the list? Yes/No")

                        def check(m):
                            return (
                                m.content.lower().strip() in ["yes", "no"] and
                                m.author == ctx.author
                            )

                        try:
                            answer = await self.bot.wait_for("messsage", timeout=15, check=check)
                        except asyncio.TimeoutError:
                            break
                        else:
                            if answer.content.lower().strip() == "yes":
                                continue
                            break
            else:
                emotes = await self._emote.guild(guild).emotes()
                istyles = sorted(emotes)
                for n in istyles:
                    cat = "|".join(c)
                    if not n[0].isalnum():
                        z = re.compile(r"\B" + n + r"\b")
                    else:
                        z = re.compile(r"\b" + n + r"\b")
                    if z.search(cat) is None:
                        missing.append(n)
                if not missing:
                    await ctx.send("All files and keywords are accounted for")
                    return
                for m in missing:
                    if m in emotes:
                        del emotes[m]
                await self._emote.guild(guild).emote.set(emotes)
                s = "\n"
                style = 10
                counter = len(missing) + 10
                while style <= counter:
                    if style <= 10:
                        y = s.join(missing[:style])
                        await ctx.send(msg + y)
                        if style >= len(missing):
                            return
                        style += 10
                    elif style > 10:
                        style2 = style - 10
                        y = s.join(missing[style2:style])
                        await ctx.send("Continuation:\n{}".format(y))
                        if style >= len(missing):
                            return
                        style += 10
                    await ctx.send("Do you want to continue seeing the list? Yes/No")

                    def check(m):
                        return (
                            m.content.lower().strip() in ["yes", "no"] and m.author == ctx.author
                        )

                    try:
                        answer = await self.bot.wait_for("messsage", timeout=15, check=check)
                    except asyncio.TimeoutError:
                        return
                    else:
                        if answer.content.lower().strip() == "yes":
                            continue
                        return

        elif style == styleset[1]:
            if alls == "all":
                servers = sorted(await self._emote.guilds())
                servers.remove("emote")
                if not c:
                    await ctx.send(
                        "It is impossible to verify the integrity of files and "
                        "keywords due to missing files. Please make sure that the"
                        " files have not been deleted."
                    )
                    return
                for servs in servers:
                    count = 0
                    server = await servs.emotes()
                    for cat in c:
                        if cat.endswith(".png"):
                            listing = cat.split(".png")
                            dog = len(listing) - 1
                            del listing[dog]
                            listing.append(".png")
                        elif cat.endswith(".gif"):
                            listing = cat.split(".gif")
                            dog = len(listing) - 1
                            del listing[dog]
                            listing.append(".gif")
                        if listing[0] not in server:
                            server[listing[0]] = cat
                            count += 1
                    if count == 0:
                        await ctx.send("All files and keywords are accounted for in " + servs)
                        if len(servers) == servers.index(servs):
                            return
                        else:
                            continue
                    await self._emote.guild(servs).emotes.set(server)
                    await ctx.send(
                        str(count) +
                        " Keywords have been successfully added to the image list in " +
                        servs
                    )
            else:
                emotes = await self._emote.guild(guild).emotes()
                if not c:
                    await ctx.send(
                        "It is impossible to verify the integrity of files and "
                        "keywords due to missing files. Please make sure that the"
                        " files have not been deleted."
                    )
                    return
                count = 0
                for cat in c:
                    listing = cat.split(".")
                    if listing[0] not in emotes:
                        emotes[listing[0]] = cat
                        count += 1
                if count == 0:
                    await ctx.send("All files and keywords are accounted for")
                    return
                await self._emote.guild(guild).emotes.set(emotes)
                await ctx.send(
                    str(count) + " Keywords have been successfully added to the image list"
                )

    async def check_emotes(self, message):
        # check if setting is on in this server
        # Let emotes happen in PMs always
        guild = message.guild
        if guild is None:
            return
        emotes = await self._emote.guild(guild).emotes()
        # Filter unauthorized users, bots and empty messages
        if not message.content:
            return

        # Don't respond to commands
        for m in await self.bot.db.prefix():
            if message.content.startswith(m):
                return

        if guild is not None:
            if not (await self._emote.guild(guild).status()):
                return

        msg = message.content.lower().split()
        listed = []
        regexen = []
        for n in sorted(emotes):
            if not n[0].isalnum():
                regexen.append(re.compile(r"\B" + n + r"\b"))
            else:
                regexen.append(re.compile(r"\b" + n + r"\b"))

        for w, r in itertools.product(msg, regexen):
            match = r.search(w)
            if match:
                listed.append(emotes[match.group(0)])

        pnglisted = list(filter(lambda n: not n.endswith(".gif"), listed))
        giflisted = list(filter(lambda n: n.endswith(".gif"), listed))
        if pnglisted and len(pnglisted) > 1:
            ims = self.imgprocess(pnglisted)
            image = self._emote_path / ims
            await message.channel.send(file=discord.File(str(image)))
        elif pnglisted:
            image = self._emote_path / pnglisted[0]
            await message.channel.send(file=discord.File(str(image)))
        if giflisted:
            for ims in giflisted:
                image = self._emote_path / ims
                await message.channel.send(file=discord.File(str(image)))

    def imgprocess(self, listed):
        for i in range(len(listed)):
            listed[i] = str(self._emote_path / listed[i])
        images = [Image.open(i) for i in listed]
        widths, heights = zip(*(i.size for i in images))
        total_width = sum(widths)
        max_height = max(heights)
        new_im = Image.new("RGBA", (total_width, max_height))
        x_offset = 0
        for im in images:
            new_im.paste(im, (x_offset, 0))
            x_offset += im.size[0]
        cat = "test.png"
        new_im.save(self._emote_path + cat)
        return cat
