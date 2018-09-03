import asyncio
import discord
from collections import OrderedDict
from operator import itemgetter

from redbot.core import Config, checks, commands
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import box

from tabulate import tabulate


class Points:
    """Point System"""

    default_guild_settings = {"bookkeeper": [], "members": {}}

    def __init__(self, bot: Red):
        self.bot = bot
        self._points = Config.get_conf(self, 4485938503)

        self._points.register_guild(**self.default_guild_settings)

    @commands.group(pass_context=True)
    async def points(self, ctx):
        """Points settings"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help()

    @points.group(pass_context=True)
    async def member(self, ctx):
        """Member settings"""
        if ctx.invoked_subcommand is None or isinstance(ctx.invoked_subcommand, commands.Group):
            await ctx.send_help()

    def permcheck(self, ctx):
        guild = ctx.guild
        author = ctx.author
        bookkeeper = self._points.guild(guild).bookkeeper()
        if author.id != guild.owner.id:
            if author.id not in bookkeeper:
                return False
            else:
                return True
        else:
            return True

    @member.command()
    async def add(self, ctx, *, name=None):
        """Adds a member to the list, defaults to author"""
        names = None
        namesp = None
        guild = ctx.guild
        if name is None:
            name = ctx.author
        elif "," in str(name):
            if ", " in name:
                names = name.split(", ")
            elif "," in name:
                names = name.split(",")
            namesp = names.copy()
            for i in range(len(names)):
                names[i] = discord.utils.find(lambda m: m.display_name == names[i], guild.members)
                if names[i] is None:
                    names[i] = discord.utils.find(lambda m: m.name == names[i], guild.members)
            name = None
        else:
            namea = name[:]
            name = discord.utils.find(lambda m: m.display_name == name, guild.members)
            if name is None:
                name = discord.utils.find(lambda m: m.name == name, guild.members)
                if name is None:
                    await ctx.send(
                        "{} was not found, please check the spelling and also make "
                        "sure that the member name being entered is a member in your Discord and "
                        "that its the same as their Discord name / nickname.".format(namea)
                    )
                    return
        members = await self._points.guild(guild).members()
        if not name:
            counter = -1
            for x in names:
                counter += 1
                if x is None:
                    await ctx.send(
                        "{} was not found, please check the spelling and also make "
                        "sure that the member name being entered is a member in your Discord and "
                        "that its the same as their Discord name / nickname.".format(
                            namesp[counter]
                        )
                    )
                    await asyncio.sleep(1)
                    continue
                elif x.id in members:
                    await ctx.send("{} is already in the list".format(x.display_name))
                elif x.id not in members:
                    members[x.id] = OrderedDict(
                        {
                            "Name": x.display_name,
                            "Balance": 0,
                            "Lifetime Gain": 0,
                            "Lifetime Loss": 0,
                        }
                    )
                    await self._points.guild(guild).members.set(members)
                    await ctx.send("{} has been added to the list.".format(x.display_name))
                await asyncio.sleep(1)

        else:
            if name.id in members:
                await ctx.send("{} is already in the list".format(name.display_name))
                return
            elif name.id not in members:
                members[name.id] = OrderedDict(
                    {
                        "Name": name.display_name,
                        "Balance": 0,
                        "Lifetime Gain": 0,
                        "Lifetime Loss": 0,
                    }
                )
                await self._points.guild(guild).members.set(members)
                await ctx.send("{} has been added to the list.".format(name.display_name))

    @member.command(pass_context=True, hidden=True)
    async def remove(self, ctx, *, name=None):
        """Deletes a member from the list, defaults to author"""
        guild = ctx.guild
        author = ctx.author
        names = None
        namesp = None
        if not self.permcheck(ctx):
            return
        if name is None:
            name = author
        elif "," in str(name):
            if ", " in name:
                names = name.split(", ")
            elif "," in name:
                names = name.split(",")
            namesp = names.copy()
            for i in range(len(names)):
                names[i] = discord.utils.find(lambda m: m.display_name == names[i], guild.members)
                if names[i] is None:
                    names[i] = discord.utils.find(lambda m: m.name == names[i], guild.members)
            name = None
        else:
            namea = name[:]
            name = discord.utils.find(lambda m: m.display_name == name, guild.members)
            if name is None:
                name = discord.utils.find(lambda m: m.name == name, guild.members)
                if name is None:
                    await ctx.send(
                        "{} was not found, please check the spelling and also make "
                        "sure that the member name being entered is a member in your Discord and "
                        "that its the same as their Discord name / nickname.".format(namea)
                    )
                    return
        members = await self._points.guild(guild).members()
        if not name:
            counter = -1
            for x in names:
                counter += 1
                if x is None:
                    await ctx.send(
                        "{} was not found, please check the spelling and also make "
                        "sure that the member name being entered is a member in your Discord and "
                        "that its the same as their Discord name / nickname.".format(
                            namesp[counter]
                        )
                    )
                    await asyncio.sleep(1)
                    continue
                elif x.id not in members:
                    await ctx.send(
                        "{} is not in the list, please make sure they have been added first to "
                        "the list.".format(x.display_name)
                    )
                elif x.id in members:
                    members.pop(x.id, None)
                    await self._points.guild(guild).members.set(members)
                    await ctx.send("{} has been removed from the list.".format(x.display_name))
                await asyncio.sleep(1)
        else:
            if name.id not in members:
                await ctx.send(
                    "{} is not in the list, please make sure they have been added first to "
                    "the list.".format(name.display_name)
                )
                return
            elif name.id in members:
                members.pop(name.id, None)
                await self._points.guild(guild).members.set(members)
                await ctx.send("{} has been deleted from the list.".format(name.display_name))

    @points.command(pass_context=True, hidden=True)
    async def reset(self, ctx):
        """Allows to wipe the guild's roster list, only usable by bookkeepers or guild owner"""
        guild = ctx.guild
        author = ctx.author
        if not self.permcheck(ctx):
            return
        await ctx.send("Are you sure? This action is irreversible. Answer yes or no")

        def check(m):
            return author == m.author

        confirmation = await self.bot.wait_for(timeout=15, check=check)
        if confirmation is None:
            await ctx.send("Action canceled.")
            return
        elif confirmation.content.lower().strip() == "yes":
            await self._points.guild(guild).clear()
            await ctx.send("The list for this guild has been reset.")
        else:
            await ctx.send("Action canceled.")
            return

    @points.command(name="add", pass_context=True)
    async def _add(self, ctx, points: int, *, name=None):
        """Adds points to a member or multiple members. Defaults to author.
           Use names, not nicknames to find them.
           Usage example:
           [p]points member add 20 fuegoscuro, aikaterna, axas, attoli"""
        guild = ctx.guild
        author = ctx.author
        names = None
        namesp = None
        members = await self._points.guild(guild).members()
        if not self.permcheck(ctx):
            return
        if name is None:
            name = author
        elif "," in str(name):
            if ", " in name:
                names = name.split(", ")
            elif "," in name:
                names = name.split(",")
            namesp = names.copy()
            for i in range(len(names)):
                names[i] = discord.utils.find(lambda m: m.display_name == names[i], guild.members)
                if names[i] is None:
                    names[i] = discord.utils.find(lambda m: m.name == names[i], guild.members)
            name = None
        else:
            namea = name[:]
            name = discord.utils.find(lambda m: m.display_name == name, guild.members)
            if name is None:
                name = discord.utils.find(lambda m: m.name == name, guild.members)
                if name is None:
                    await ctx.send(
                        "{} was not found, please check the spelling and also make "
                        "sure that the member name being entered is a member in your Discord and "
                        "that its the same as their Discord name / nickname.".format(namea)
                    )
                    return
        if not name:
            counter = -1
            for x in names:
                counter += 1
                if x is None:
                    await ctx.send(
                        "{} was not found, please check the spelling and also make "
                        "sure that the member name being entered is a member in your Discord and "
                        "that its the same as their Discord name / nickname.".format(
                            namesp[counter]
                        )
                    )
                    await asyncio.sleep(1)
                    continue
                elif x.id not in self._points.guild(guild).members():
                    await ctx.send(
                        "{} was not found. Please add them first using points member add"
                        " <discord name or Nickname>".format(x.display_name)
                    )
                else:
                    members[x.id]["Lifetime Gain"] += points
                    members[x.id]["Balance"] += points
                    await ctx.send("{} points added for {}".format(points, x.name))
                await asyncio.sleep(1)
        else:
            if name.id not in self._points.guild(guild).members():
                await ctx.send(
                    "{} is not in the list, please register first using points member add"
                    " <Discord name or nickname>".format(namea)
                )
                return
            members[name.id]["Lifetime Gain"] += points
            members[name.id]["Balance"] += points
            await ctx.send("{} points added for {}".format(points, name.name))
        await self._points.guild(guild).members.set(members)

    @points.command(name="remove", pass_context=True)
    async def _remove(self, ctx, points: int, *, name=None):
        """Takes away points from a member or multiple members. Defaults to author
           Usage example:
           [p]points member remove 20 fuegoscuro, aikaterna, axas, attoli"""
        guild = ctx.guild
        author = ctx.author
        names = None
        members = await self._points.guild(guild).members()
        if not self.permcheck(ctx):
            return
        if name is None:
            name = author
        elif "," in str(name):
            if ", " in name:
                names = name.split(", ")
            elif "," in name:
                names = name.split(",")
            namesp = names.copy()
            for i in range(len(names)):
                names[i] = discord.utils.find(lambda m: m.display_name == names[i], guild.members)
                if names[i] is None:
                    names[i] = discord.utils.find(lambda m: m.name == names[i], guild.members)
            name = None
        else:
            namea = name[:]
            name = discord.utils.find(lambda m: m.display_name == name, guild.members)
            if name is None:
                name = discord.utils.find(lambda m: m.name == name, guild.members)
                if name is None:
                    await ctx.send(
                        "{} was not found, please check the spelling and also make "
                        "sure that the member name being entered is a member in your Discord and "
                        "that its the same as their Discord name / nickname.".format(namea)
                    )
                    return
        if not name:
            counter = -1
            for x in names:
                counter += 1
                if x is None:
                    await ctx.send(
                        "{} was not found, please check the spelling and also make "
                        "sure that the member name being entered is a member in your Discord and "
                        "that its the same as their Discord name / nickname.".format(
                            namesp[counter]
                        )
                    )
                    await asyncio.sleep(1)
                    continue
                elif x.id not in members:
                    await ctx.send(
                        "{} was not found. Please add them first using points member add"
                        " <discord name or Nickname>".format(x.display_name)
                    )
                else:

                    members[x.id]["Lifetime Loss"] += points
                    members[x.id]["Balance"] -= points
                    await ctx.send("{} points substracted from {}".format(points, x.name))
                await asyncio.sleep(1)
        else:
            if name.id not in members:
                await ctx.send(
                    "{} is not in the list, please register first using points member add"
                    " <Discord name or nickname>".format(namea)
                )
                return
            members[name.id]["Lifetime Loss"] += points
            members[name.id]["Balance"] -= points
            await ctx.send("{} points substracted from {}".format(points, name.name))
        await self._points.guild(guild).members.set(members)

    @points.command(name="list", pass_context=True)
    async def _list(self, ctx):
        """Allows to show the balance of all the registered users."""
        guild = ctx.guild
        db = await self._points.guild(guild).members()
        if len(db) < 1:
            await ctx.send(
                "List is empty, please add members first using [p]points add <Discord name or nickname>"
            )
            return
        try:
            columns = [sorted([y for y in db[x].keys()], reverse=True) for x in db][0]
            i, j = columns.index(columns[1]), columns.index(columns[2])
            columns[i], columns[j] = columns[j], columns[i]
            rows = sorted(
                [
                    [
                        db[x]["Name"],
                        db[x]["Lifetime Gain"],
                        db[x]["Lifetime Loss"],
                        db[x]["Balance"],
                    ]
                    for x in db
                ],
                key=itemgetter(3, 0),
                reverse=True,
            )
        except IndexError:
            await ctx.send(
                "No one has been added to the list, please use points member add"
                " <Discord name or nickname> to do so first."
            )
            return
        if len(rows) > 15:
            n = 14
            l = 15
            m = 0

            for x in range(n, len(rows) + 15, l):
                if x == n:
                    await ctx.send(box(tabulate(rows[:x], headers=columns), lang="prolog"))
                else:
                    await ctx.send(box(tabulate(rows[m:x], headers=columns), lang="prolog"))
                m = x
        else:
            await ctx.send(box(tabulate(rows, headers=columns), lang="prolog"))

    @points.command(pass_context=True)
    async def balance(self, ctx, name: discord.Member = None):
        """Allows to show the balance of a user. Defaults to author."""
        guild = ctx.guild
        author = ctx.author
        members = await self._points.guild(guild).members()
        print(name)
        if name is None:
            name = author
        if str(name.id) not in members.keys():
            await ctx.send(
                "{} was not found. "
                "Please add them first using points member add"
                " <Discord name or nickname>".format(name.display_name)
            )
            return
        else:
            gain = members[str(name.id)]["Lifetime Gain"]
            loss = members[str(name.id)]["Lifetime Loss"]
            balance = members[str(name.id)]["Balance"]
            await ctx.send(
                "{} has a current balance of {} points. "
                "Their lifetime gain is {} and lifetime loss is {}.".format(
                    name.display_name, balance, gain, loss
                )
            )

    @points.group(pass_context=True)
    @checks.guildowner()
    async def keeper(self, ctx):
        """bookkeeper settings"""
        if ctx.invoked_subcommand is None or isinstance(ctx.invoked_subcommand, commands.Group):
            await ctx.send_help()

    @keeper.command(name="add", pass_context=True)
    async def __add(self, ctx, name: discord.Member = None):
        """Adds a bookkeeper to the bookkeeping list.
           This allows them to handle things such as adding/removing points/members and resetting the roster"""
        guild = ctx.guild
        author = ctx.author
        bookkeeper = await self._points.guild(guild).bookkeeper()
        if name is None:
            name = author
        if name.id in bookkeeper:
            await ctx.send("{} is already registered as a bookkeeper".format(name.display_name))
        else:
            bookkeeper.append(name.id)
        await self._points.guild(guild).bookkeeper.set(bookkeeper)
        await ctx.send("{} has been registered as a bookkeeper.".format(name.display_name))

    @keeper.command(name="remove", pass_context=True)
    async def __remove(self, ctx, name: discord.Member = None):
        """Removes a bookkeeper from the bookkeeping list"""
        guild = ctx.guild
        author = ctx.author
        bookkeeper = await self._points.guild(guild).bookkeeper()
        if name is None:
            name = author
        if len(bookkeeper) < 1:
            await ctx.send(
                "Bookkeeper list is currently empty, add new bookkeepers using points keeper add"
                " <Discord name or nickname>"
            )
            return
        if name.id not in bookkeeper:
            await ctx.send(
                "Keeper is not registered, please make sure the name or nickname is correctly spelled. "
                "You can check using points keeper list"
            )
            return
        bookkeeper.remove(name.id)
        await self._points.guild(guild).bookkeeper.set(bookkeeper)
        await ctx.send("{} has been removed from the list of bookkeepers")

    @keeper.command(name="list", pass_context=True)
    async def __list(self, ctx):
        """Shows the current list of bookkeepers"""
        guild = ctx.guild
        bookkeeper = await self._points.guild(guild).bookkeeper()
        if len(bookkeeper) < 1:
            await ctx.send(
                "Bookkeeper list is currently empty, add new bookkeepers using points keeper add"
                " <Discord name or nickname>"
            )
            return
        msg = ""
        for x in bookkeeper:
            bookkeeper[bookkeeper.index(x)] = discord.utils.find(
                lambda N: N.id == x, guild.members
            ).display_name
        bookkeeper = sorted(
            bookkeeper,
            key=lambda item: (
                int(item.partition(" ")[0]) if item[0].isdigit() else float("inf"),
                item,
            ),
        )
        msg = ", ".join(bookkeeper[:-2] + [" and ".join(bookkeeper[-2:])])
        await ctx.send("Current bookkeepers assigned are: {}".format(msg))
