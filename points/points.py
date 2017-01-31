import discord
import os
from discord.ext import commands
from cogs.utils import checks
from cogs.utils.dataIO import dataIO
from cogs.utils.chat_formatting import box
from collections import OrderedDict
from operator import itemgetter

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

    @commands.command(pass_context=True)
    async def add_member(self, ctx, *, name=None):
        """Adds a member to the list, defaults to author"""
        server = ctx.message.server
        author = ctx.message.author
        names = None
        if name is None:
            name = author
        elif "," in str(name):
            if ", " in name:
                names = name.split(", ")
            elif "," in name:
                names = name.split(",")
            for i in range(len(names)):
                names[i] = discord.utils.find(
                    lambda m: m.display_name == names[i], server.members)
                if names[i] is None:
                    names[i] = discord.utils.find(
                        lambda m: m.name == names[i], server.members)
            name = None
        else:
            name = discord.utils.find(
                lambda m: m.display_name == name, server.members)
            if name is None:
                name = discord.utils.find(
                    lambda m: m.name == name, server.members)
        if server.id not in self.db:
            self.db[server.id] = {}
        if not name:
            for x in names:
                if x.id in self.db[server.id]:
                    await self.bot.say("Member already exists.")
                elif x.id not in self.db[server.id]:
                    self.db[server.id][x.id] = OrderedDict(
                        {"Name": x.display_name, "Balance": 0, "Lifetime Gain": 0, "Lifetime Loss": 0})
                    self.save_db()
                    await self.bot.say("Member has been added.")
        else:
            if name.id in self.db[server.id]:
                await self.bot.say("Member already exists.")
                return
            elif name.id not in self.db[server.id]:
                self.db[server.id][name.id] = OrderedDict(
                    {"Name": name.display_name, "Balance": 0, "Lifetime Gain": 0, "Lifetime Loss": 0})
                self.save_db()
                await self.bot.say("Member has been added.")

    @checks.is_owner()
    @commands.command(pass_context=True, hidden=True)
    async def del_member(self, ctx, *, name=None):
        """Deletes a member from the list, defaults to author"""
        server = ctx.message.server
        author = ctx.message.author
        names = None
        if name is None:
            name = author
        elif "," in str(name):
            if ", " in name:
                names = name.split(", ")
            elif "," in name:
                names = name.split(",")
            for i in range(len(names)):
                    names[i] = discord.utils.find(lambda m: m.display_name == names[i], server.members)
                    if names[i] is None:
                        names[i] = discord.utils.find(lambda m: m.name == names[i], server.members)
            name = None
        else:
            name = discord.utils.find(lambda m: m.display_name == name, server.members)
            if name is None:
                name = discord.utils.find(lambda m: m.name == name, server.members)
        if server.id not in self.db:
            self.db[server.id] = {}
        if not name:
            for x in names:
                if x.id not in self.db[server.id]:
                    await self.bot.say("User does not exist, please make sure they have been added first to the list.")
                elif x.id in self.db[server.id]:
                    del self.db[server.id][x.id]
                    self.save_db()
                    await self.bot.say("Member has been deleted.")
        else:
            if name.id not in self.db[server.id]:
                    await self.bot.say("User does not exist, please make sure they have been added first to the list.")
                    return
            elif name.id in self.db[server.id]:
                del self.db[server.id][name.id]
                self.save_db()
                await self.bot.say("Member has been deleted.")

    @checks.admin_or_permissions(administrator=True)
    @commands.command(pass_context=True)
    async def add_points(self, ctx, points: int, *, name=None):
        """Adds points to a member or multiple members. Defaults to author.
           Use names, not nicknames to find them.
           Usage example:
           [p]add_points 20 fuegoscuro, aikaterna, axas, attoli"""
        server = ctx.message.server
        author = ctx.message.author
        names = None
        if name is None:
            name = author
        elif "," in str(name):
            if ", " in name:
                names = name.split(", ")
            elif "," in name:
                names = name.split(",")
            for i in range(len(names)):
                names[i] = discord.utils.find(
                    lambda m: m.display_name == names[i], server.members)
                if names[i] is None:
                    names[i] = discord.utils.find(
                        lambda m: m.name == names[i], server.members)
            name = None
        else:
            name = discord.utils.find(
                lambda m: m.display_name == name, server.members)
            if name is None:
                name = discord.utils.find(
                    lambda m: m.name == name, server.members)
        if server.id not in self.db:
            self.db[server.id] = {}
        if not name:
            for x in names:
                if x.id not in self.db[server.id] or x is None:
                    await self.bot.say("{} was not found. Please add them first "
                                       "using add_member. If they exist, check that the "
                                       "name was spelled correctly.".format(x.display_name))
                    continue
                else:
                    self.db[server.id][x.id]["Lifetime Gain"] += points
                    self.db[server.id][x.id]["Balance"] += points
                    await self.bot.say("Points added for {}".format(x.name))
        else:
            self.db[server.id][name.id]["Lifetime Gain"] += points
            self.db[server.id][name.id]["Balance"] += points
            await self.bot.say("Points added for {}".format(name.name))
        self.save_db()

    @checks.admin_or_permissions(administrator=True)
    @commands.command(pass_context=True)
    async def del_points(self, ctx, points: int, *, name=None):
        """Takes away points from a member or multiple members. Defaults to author
           Usage example:
           [p]add_points 20 fuegoscuro, aikaterna, axas, attoli"""
        server = ctx.message.server
        author = ctx.message.author
        names = None
        if name is None:
            name = author
        elif "," in str(name):
            if ", " in name:
                names = name.split(", ")
                namesp = names.copy()
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
            name = discord.utils.find(
                lambda m: m.display_name == name, server.members)
            if name is None:
                name = discord.utils.find(
                    lambda m: m.name == name, server.members)
        if server.id not in self.db:
            self.db[server.id] = {}
        if not name:
            for x in names:
                if x is None:
                    await self.bot.say("{} was not found. Please add them first using "
                                       "add_member".format(namesp[names.index(x)]))
                    continue
                else:
                    self.db[server.id][x.id]["Lifetime Loss"] += points
                    self.db[server.id][x.id]["Balance"] -= points
                    await self.bot.say("Points substracted from {}".format(x.name))
        else:
            self.db[server.id][name.id]["Lifetime Loss"] += points
            self.db[server.id][name.id]["Balance"] -= points
            await self.bot.say("Points substracted from {}".format(name.name))
        self.save_db()

    @commands.command(pass_context=True)
    async def balance(self, ctx, name: discord.Member=None):
        """Allows to show the balance of a user. Defaults to author."""
        server = ctx.message.server
        author = ctx.message.author
        if name is None:
            name = author
        if server.id not in self.db:
            self.db[server.id] = {}
        if name.id not in self.db[server.id]:
            await self.bot.say("{} was not found. Please add them first using add_member".format(name.display_name))
            return
        else:
            gain = self.db[server.id][name.id]["Lifetime Gain"]
            loss = self.db[server.id][name.id]["Lifetime Loss"]
            balance = self.db[server.id][name.id]["Balance"]
            await self.bot.say("{} has a current balance of {} points. Their lifetime gain is {} and "
                               "lifetime loss is {}.".format(name.display_name, balance, gain, loss))

    @commands.command(pass_context=True)
    async def balance_all(self, ctx):
        """Allows to show the balance of all the registered users."""
        server = ctx.message.server
        if server.id not in self.db:
            self.db[server.id] = {}
            self.save_db()
        else:
            db = self.db[server.id]
        try:
            columns = [sorted([y for y in self.db[server.id][x].keys()], reverse=True) for x in self.db[server.id]][0]
            i, j = columns.index(columns[1]), columns.index(columns[2])
            columns[i], columns[j] = columns[j], columns[i]
            rows = sorted([[db[x]["Name"], db[x]["Lifetime Gain"], db[x]["Lifetime Loss"], db[x]["Balance"]]
                          for x in db], key=itemgetter(3, 0), reverse=True)
        except IndexError:
            await self.bot.say("No one has been added to the list, please use add_member to do so first.")
            return
        if len(rows) > 15:
            n = 14
            l = 15
            m = 0
            for x in range(n, n*3, l):
                if x == n:
                    await self.bot.say(box(tabulate(rows[:x], headers=columns), lang="prolog"))
                elif x != n:
                    await self.bot.say(box(tabulate(rows[m:x], headers=columns), lang="prolog"))
                elif x > len(rows):
                    return
                m = x
        else:
            await self.bot.say(box(tabulate(rows, headers=columns), lang="prolog"))


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
