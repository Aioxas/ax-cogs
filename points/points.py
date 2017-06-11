import asyncio
import discord
import os
from discord.ext import commands
from cogs.utils import checks
from cogs.utils.dataIO import dataIO
from cogs.utils.chat_formatting import box
from collections import OrderedDict
from operator import itemgetter
from __main__ import send_cmd_help

try:
    from tabulate import tabulate
    Tabulate = True
except:
    Tabulate = False


class Points:
    """Point System"""

    def __init__(self, bot):
        self.bot = bot
        self.path = "data/points/db.json"
        self.db = dataIO.load_json(self.path)

    def save_db(self):
        dataIO.save_json(self.path, self.db)

    @commands.group(pass_context=True)
    async def points(self, ctx):
        """Points settings"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @points.group(pass_context=True)
    async def member(self, ctx):
        """Member settings"""
        if ctx.invoked_subcommand is None or \
                isinstance(ctx.invoked_subcommand, commands.Group):
            await send_cmd_help(ctx)

    def permcheck(self, ctx):
        server = ctx.message.server
        author = ctx.message.author
        if "bookkeeper" in self.db[server.id]:
            bookkeeper = self.db[server.id]["bookkeeper"]
        else:
            self.db[server.id]["bookkeeper"] = []
            self.save_db()
            bookkeeper = []
        if author.id != server.owner.id:
            if author.id not in bookkeeper:
                return False
            else:
                return True
        else:
            return True

    @member.command(pass_context=True)
    async def add(self, ctx, *, name=None):
        """Adds a member to the list, defaults to author"""
        server = ctx.message.server
        author = ctx.message.author
        names = None
        namesp = None
        if name is None:
            name = author
        elif "," in str(name):
            if ", " in name:
                names = name.split(", ")
            elif "," in name:
                names = name.split(",")
            namesp = names.copy()
            for i in range(len(names)):
                names[i] = discord.utils.find(
                    lambda m: m.display_name == names[i], server.members)
                if names[i] is None:
                    names[i] = discord.utils.find(
                        lambda m: m.name == names[i], server.members)
            name = None
        else:
            namea = name[:]
            name = discord.utils.find(
                lambda m: m.display_name == name, server.members)
            if name is None:
                name = discord.utils.find(
                    lambda m: m.name == name, server.members)
                if name is None:
                    await self.bot.say("{} was not found, please check the spelling and also make "
                                       "sure that the member name being entered is a member in your Discord and "
                                       "that its the same as their Discord name / nickname.".format(namea))
                    return
        if server.id not in self.db:
            self.db[server.id] = {}
        if not name:
            counter = -1
            for x in names:
                counter += 1
                if x is None:
                    await self.bot.say("{} was not found, please check the spelling and also make "
                                       "sure that the member name being entered is a member in your Discord and "
                                       "that its the same as their Discord name / nickname.".format(namesp[counter]))
                    await asyncio.sleep(1)
                    continue
                elif x.id in self.db[server.id]:
                    await self.bot.say("{} is already in the list".format(x.display_name))
                elif x.id not in self.db[server.id]:
                    self.db[server.id][x.id] = OrderedDict(
                        {"Name": x.display_name, "Balance": 0, "Lifetime Gain": 0, "Lifetime Loss": 0})
                    self.save_db()
                    await self.bot.say("{} has been added to the list.".format(x.display_name))
                await asyncio.sleep(1)

        else:
            if name.id in self.db[server.id]:
                await self.bot.say("{} is already in the list".format(name.display_name))
                return
            elif name.id not in self.db[server.id]:
                self.db[server.id][name.id] = OrderedDict(
                    {"Name": name.display_name, "Balance": 0, "Lifetime Gain": 0, "Lifetime Loss": 0})
                self.save_db()
                await self.bot.say("{} has been added to the list.".format(name.display_name))

    @member.command(pass_context=True, hidden=True)
    async def remove(self, ctx, *, name=None):
        """Deletes a member from the list, defaults to author"""
        server = ctx.message.server
        author = ctx.message.author
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
                    names[i] = discord.utils.find(lambda m: m.display_name == names[i], server.members)
                    if names[i] is None:
                        names[i] = discord.utils.find(lambda m: m.name == names[i], server.members)
            name = None
        else:
            namea = name[:]
            name = discord.utils.find(lambda m: m.display_name == name, server.members)
            if name is None:
                name = discord.utils.find(lambda m: m.name == name, server.members)
                if name is None:
                    await self.bot.say("{} was not found, please check the spelling and also make "
                                       "sure that the member name being entered is a member in your Discord and "
                                       "that its the same as their Discord name / nickname.".format(namea))
                    return
        if server.id not in self.db:
            self.db[server.id] = {}
        if not name:
            counter = -1
            for x in names:
                counter += 1
                if x is None:
                    await self.bot.say("{} was not found, please check the spelling and also make "
                                       "sure that the member name being entered is a member in your Discord and "
                                       "that its the same as their Discord name / nickname.".format(namesp[counter]))
                    await asyncio.sleep(1)
                    continue
                elif x.id not in self.db[server.id]:
                    await self.bot.say("{} is not in the list, please make sure they have been added first to "
                                       "the list.".format(x.display_name))
                elif x.id in self.db[server.id]:
                    del self.db[server.id][x.id]
                    self.save_db()
                    await self.bot.say("{} has been removed from the list.".format(x.display_name))
                await asyncio.sleep(1)
        else:
            if name.id not in self.db[server.id]:
                    await self.bot.say("{} is not in the list, please make sure they have been added first to "
                                       "the list.".format(name.display_name))
                    return
            elif name.id in self.db[server.id]:
                del self.db[server.id][name.id]
                self.save_db()
                await self.bot.say("{} has been deleted from the list.".format(name.display_name))

    @points.command(pass_context=True, hidden=True)
    async def reset(self, ctx):
        """Allows to wipe the server's roster list, only usable by bookkeepers or server owner"""
        server = ctx.message.server
        author = ctx.message.author
        if not self.permcheck(ctx):
            return
        await self.bot.say("Are you sure? This action is irreversible. Answer yes or no")
        confirmation = await self.bot.wait_for_message(timeout=15, author=author)
        if confirmation is None:
            await self.bot.say("Action canceled.")
            return
        elif confirmation.content.lower().strip() == "yes":
            self.db[server.id] = {}
            self.save_db()
            await self.bot.say("The list for this server has been reset.")
        else:
            await self.bot.say("Action canceled.")
            return

    @points.command(name="add", pass_context=True)
    async def _add(self, ctx, points: int, *, name=None):
        """Adds points to a member or multiple members. Defaults to author.
           Use names, not nicknames to find them.
           Usage example:
           [p]points member add 20 fuegoscuro, aikaterna, axas, attoli"""
        server = ctx.message.server
        author = ctx.message.author
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
                names[i] = discord.utils.find(
                    lambda m: m.display_name == names[i], server.members)
                if names[i] is None:
                    names[i] = discord.utils.find(
                        lambda m: m.name == names[i], server.members)
            name = None
        else:
            namea = name[:]
            name = discord.utils.find(
                lambda m: m.display_name == name, server.members)
            if name is None:
                name = discord.utils.find(
                    lambda m: m.name == name, server.members)
                if name is None:
                    await self.bot.say("{} was not found, please check the spelling and also make "
                                       "sure that the member name being entered is a member in your Discord and "
                                       "that its the same as their Discord name / nickname.".format(namea))
                    return
        if server.id not in self.db:
            self.db[server.id] = {}
        if not name:
            counter = -1
            for x in names:
                counter += 1
                if x is None:
                    await self.bot.say("{} was not found, please check the spelling and also make "
                                       "sure that the member name being entered is a member in your Discord and "
                                       "that its the same as their Discord name / nickname.".format(namesp[counter]))
                    await asyncio.sleep(1)
                    continue
                elif x.id not in self.db[server.id]:
                    await self.bot.say("{} was not found. Please add them first using points member add"
                                       " <discord name or Nickname>".format(x.display_name))
                else:
                    self.db[server.id][x.id]["Lifetime Gain"] += points
                    self.db[server.id][x.id]["Balance"] += points
                    await self.bot.say("{} points added for {}".format(points, x.name))
                await asyncio.sleep(1)
        else:
            if name.id not in self.db[server.id]:
                await self.bot.say("{} is not in the list, please register first using points member add"
                                   " <Discord name or nickname>".format(namea))
                return
            self.db[server.id][name.id]["Lifetime Gain"] += points
            self.db[server.id][name.id]["Balance"] += points
            await self.bot.say("{} points added for {}".format(points, name.name))
        self.save_db()

    @points.command(name="remove", pass_context=True)
    async def _remove(self, ctx, points: int, *, name=None):
        """Takes away points from a member or multiple members. Defaults to author
           Usage example:
           [p]points member remove 20 fuegoscuro, aikaterna, axas, attoli"""
        server = ctx.message.server
        author = ctx.message.author
        names = None
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
                names[i] = discord.utils.find(
                    lambda m: m.display_name == names[i], server.members)
                if names[i] is None:
                    names[i] = discord.utils.find(
                        lambda m: m.name == names[i], server.members)
            name = None
        else:
            namea = name[:]
            name = discord.utils.find(
                lambda m: m.display_name == name, server.members)
            if name is None:
                name = discord.utils.find(
                    lambda m: m.name == name, server.members)
                if name is None:
                    await self.bot.say("{} was not found, please check the spelling and also make "
                                       "sure that the member name being entered is a member in your Discord and "
                                       "that its the same as their Discord name / nickname.".format(namea))
                    return
        if server.id not in self.db:
            self.db[server.id] = {}
        if not name:
            counter = -1
            for x in names:
                counter += 1
                if x is None:
                    await self.bot.say("{} was not found, please check the spelling and also make "
                                       "sure that the member name being entered is a member in your Discord and "
                                       "that its the same as their Discord name / nickname.".format(namesp[counter]))
                    await asyncio.sleep(1)
                    continue
                elif x.id not in self.db[server.id]:
                    await self.bot.say("{} was not found. Please add them first using points member add"
                                       " <discord name or Nickname>".format(x.display_name))
                else:
                    self.db[server.id][x.id]["Lifetime Loss"] += points
                    self.db[server.id][x.id]["Balance"] -= points
                    await self.bot.say("{} points substracted from {}".format(points, x.name))
                await asyncio.sleep(1)
        else:
            if name.id not in self.db[server.id]:
                await self.bot.say("{} is not in the list, please register first using points member add"
                                   " <Discord name or nickname>".format(namea))
                return
            self.db[server.id][name.id]["Lifetime Loss"] += points
            self.db[server.id][name.id]["Balance"] -= points
            await self.bot.say("{} points substracted from {}".format(points, name.name))
        self.save_db()

    @points.command(name="list", pass_context=True)
    async def _list(self, ctx):
        """Allows to show the balance of all the registered users."""
        server = ctx.message.server
        if server.id not in self.db:
            self.db[server.id] = {}
            self.save_db()
            await self.bot.say("List is empty, please add members first using [p]points add <Discord name or nickname>")
            return
        else:
            db = self.db[server.id]
        try:
            columns = [sorted([y for y in self.db[server.id][x].keys()], reverse=True)
                       for x in db if x != "bookkeeper"][0]
            i, j = columns.index(columns[1]), columns.index(columns[2])
            columns[i], columns[j] = columns[j], columns[i]
            rows = sorted([[db[x]["Name"], db[x]["Lifetime Gain"], db[x]["Lifetime Loss"], db[x]["Balance"]]
                           for x in db if x != "bookkeeper"], key=itemgetter(3, 0), reverse=True)
        except IndexError:
            await self.bot.say("No one has been added to the list, please use points member add"
                               " <Discord name or nickname> to do so first.")
            return
        if len(rows) > 15:
            n = 14
            l = 15
            m = 0

            for x in range(n, len(rows)+15, l):
                if x == n:
                    await self.bot.say(box(tabulate(rows[:x], headers=columns), lang="prolog"))
                else:
                    await self.bot.say(box(tabulate(rows[m:x], headers=columns), lang="prolog"))
                m = x
        else:
            await self.bot.say(box(tabulate(rows, headers=columns), lang="prolog"))

    @points.command(pass_context=True)
    async def balance(self, ctx, name: discord.Member=None):
        """Allows to show the balance of a user. Defaults to author."""
        server = ctx.message.server
        author = ctx.message.author
        if name is None:
            name = author
        if server.id not in self.db:
            self.db[server.id] = {}
        if name.id not in self.db[server.id]:
            await self.bot.say("{} was not found. "
                               "Please add them first using points member add"
                               " <Discord name or nickname>".format(name.display_name))
            return
        else:
            gain = self.db[server.id][name.id]["Lifetime Gain"]
            loss = self.db[server.id][name.id]["Lifetime Loss"]
            balance = self.db[server.id][name.id]["Balance"]
            await self.bot.say("{} has a current balance of {} points. "
                               "Their lifetime gain is {} and lifetime loss is {}."
                               .format(name.display_name, balance, gain, loss))

    @points.group(pass_context=True)
    @checks.serverowner()
    async def keeper(self, ctx):
        """bookkeeper settings"""
        if ctx.invoked_subcommand is None or \
                isinstance(ctx.invoked_subcommand, commands.Group):
            await send_cmd_help(ctx)

    @keeper.command(name="add", pass_context=True)
    async def __add(self, ctx, name: discord.Member=None):
        """Adds a bookkeeper to the bookkeeping list.
           This allows them to handle things such as adding/removing points/members and resetting the roster"""
        server = ctx.message.server
        author = ctx.message.author
        if name is None:
            name = author
        if server.id not in self.db:
            self.db[server.id] = {}
        if "bookkeeper" not in self.db[server.id]:
            self.db[server.id]["bookkeeper"] = []
        if name.id in self.db[server.id]["bookkeeper"]:
            await self.bot.say("{} is already registered as a bookkeeper".format(name.display_name))
        else:
            self.db[server.id]["bookkeeper"].append(name.id)
        self.save_db()
        await self.bot.say("{} has been registered as a bookkeeper.".format(name.display_name))

    @keeper.command(name="remove", pass_context=True)
    async def __remove(self, ctx, name: discord.Member=None):
        """Removes a bookkeeper from the bookkeeping list"""
        server = ctx.message.server
        author = ctx.message.author
        if name is None:
            name = author
        if server.id not in self.db:
            self.db[server.id] = {}
        if "bookkeeper" not in self.db[server.id]:
            self.db[server.id]["bookkeeper"] = []
            await self.bot.say("Bookkeeper list is currently empty, add new bookkeepers using points keeper add"
                               " <Discord name or nickname>")
            self.save_db()
            return
        if name.id not in self.db[server.id]["bookkeeper"]:
            await self.bot.say("Keeper is not registered, please make sure the name or nickname is correctly spelled. "
                               "You can check using points keeper list")
            return
        self.db[server.id]["bookkeeper"].remove(name.id)
        self.save_db()

    @keeper.command(name="list", pass_context=True)
    async def __list(self, ctx):
        """Shows the current list of bookkeepers"""
        server = ctx.message.server
        if server.id not in self.db:
            self.db[server.id] = {}
            self.save_db()
        else:
            db = self.db[server.id]
        if "bookkeeper" not in self.db[server.id]:
            self.db[server.id]["bookkeeper"] = []
            self.save_db()
            await self.bot.say("Bookkeeper list is currently empty, add new bookkeepers using points keeper add"
                               " <Discord name or nickname>")
            return
        else:
            bookkeeper = db["bookkeeper"][:]
        msg = ""
        for x in bookkeeper:
            bookkeeper[bookkeeper.index(x)] = discord.utils.find(lambda N: N.id == x, server.members).display_name
        bookkeeper = sorted(bookkeeper, key=lambda item: (int(item.partition(' ')[0])
                                                          if item[0].isdigit() else float('inf'), item))
        msg = ", ".join(bookkeeper[:-2] + [" and ".join(bookkeeper[-2:])])
        await self.bot.say("Current bookkeepers assigned are: {}".format(msg))


def check_folders():
    f = "data/points"
    if not os.path.exists(f):
        print("creating data/points directory")
        os.mkdir(f)


def check_files():
    f = 'data/points/db.json'
    if not os.path.isfile(f):
        default = {}
        print('Creating default points/db.json...')
        dataIO.save_json(f, default)


def setup(bot):
    if Tabulate:
        check_folders()
        check_files()
        bot.add_cog(Points(bot))
    else:
        raise RuntimeError("You need to run 'pip3 install tabulate'")
