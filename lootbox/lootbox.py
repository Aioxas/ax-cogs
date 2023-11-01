import numpy
import os

from __main__ import send_cmd_help
from .utils import checks
from .utils.chat_formatting import pagify
from .utils.dataIO import dataIO
from discord.ext import commands


class Lootbox:

    def __init__(self, bot):
        self.bot = bot
        self.db = dataIO.load_json("data/lootbox/servers.json")

    @commands.group(pass_context=True)
    async def box(self, ctx):
        """Box related commands"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @box.command(pass_context=True)
    async def add(self, ctx, name: str, content: str, multi: int=None):
        """Adds items to a box
           Usage:
           winter = box name
           [p]box add winter Key 20
           [p]box add winter "Key, Unsealing Charm" 20"""
        name = name.lower()
        server = ctx.message.server
        counter = 0
        neg = False
        if server.id not in self.db:
            self.db[server.id] = {}
        if name not in self.db[server.id]:
            await self.bot.say("Box doesn't exist, please use [p]box create first")
            return
        if ", " in content:
            content = content.split(", ")
        elif "," in content:
            content = content.split(",")
        if multi < 0:
            neg = True
            multi = abs(multi)
        if multi and type(content) is not list:
            content = [content.lower()] * multi
        else:
            content = content * multi
        print(content)
        for x in content:
            x = x.lower()
            if x in self.db[server.id][name]["content"]:
                if neg:
                    self.db[server.id][name]["content"][x] -= 1
                else:
                    self.db[server.id][name]["content"][x] += 1
            else:
                counter += 1
                continue
        dataIO.save_json("data/lootbox/servers.json", self.db)
        await self.bot.say("Items added to {} box: {}. Items failed to add: "
                           "{}".format(name, len(content)-counter, counter))

    @box.command(pass_context=True)
    async def create(self, ctx, name: str, output: int, *, content: str):
        """Creates a box in the current server
           [p]box create winter 6 Key, Unsealing Charm, Black Padded Coat, Infernal Horn"""
        name = name.lower()
        server = ctx.message.server
        if server.id not in self.db:
            self.db[server.id] = {}
        if name in self.db[server.id]:
            await self.bot.say("Box already exists, please use another name or use box edit to change the contents")
            return
        if ", " in content:
            content = content.split(", ")
        elif "," in content:
            content = content.split(",")
        self.db[server.id][name] = {"content": {}, "output": output}
        for x in content:
            x = x.lower()
            self.db[server.id][name]["content"][x] = 0
        dataIO.save_json("data/lootbox/servers.json", self.db)
        await self.bot.say("{} box has been added, it has {} items and outputs {}"
                           " items".format(name, len(content), output))

    @checks.mod_or_permissions()
    @box.group(pass_context=True)
    async def edit(self, ctx):
        """Allows editing of box names or output"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @edit.command(pass_context=True)
    async def name(self, ctx, name: str, newname: str):
        """Allows editing of the boxes' name
           winter = current name
           autumn = new name
           [p]box edit name winter autumn"""
        name = name.lower()
        newname = newname.lower()
        server = ctx.message.server
        if server.id not in self.db:
            self.db[server.id] = {}
        if newname in self.db[server.id]:
            await self.bot.say("Box already exists, please use another name")
            return
        if name not in self.db[server.id]:
            await self.bot.say("Box doesn't exist, please make sure the spelling is correct and"
                               " that it's found in [p]box list")
            return
        self.db[server.id][newname] = self.db[server.id].pop(name, None)
        dataIO.save_json("data/lootbox/servers.json", self.db)
        await self.bot.say("{} has been renamed to {}".format(name, newname))

    @edit.command(pass_context=True)
    async def output(self, ctx, name: str, output: int):
        """Allows adjusting how many items
           come out of the simulated lootbox
           [p]box edit output 20"""
        server = ctx.message.server
        if server.id not in self.db:
            self.db[server.id] = {}
        if name not in self.db[server.id]:
            await self.bot.say("Box doesn't exist, please make sure the spelling is correct and"
                               " that it's found in [p]box list")
            return
        self.db[server.id][name]["output"] = output
        dataIO.save_json("data/lootbox/servers.json", self.db)
        await self.bot.say("{} box's output has changed to {}".format(name, output))

    @edit.command(pass_context=True)
    async def append(self, ctx, name: str, items: str):
        """Allows adding new items to an already created lootbox
           [p]box edit append "item_1 1, item_2 4, item_3 5"
           Names are fixed when they are added."""
        server = ctx.message.server
        items = items.split(", ")
        itemis = {}
        for item in items:
            item, value = item.split(" ")
            item = item.replace("_", " ").lower()
            itemis[item] = value
        if server.id not in self.db:
            self.db[server.id] = {}
        if name not in self.db[server.id]:
            await self.bot.say("Box doesn't exist, please make sure the spelling is correct and"
                               " that it's found in [p]box list")
            return
        items = list(itemis.keys())
        for item in items:
            value = itemis[item]
            if item in self.db[server.id][name]["content"]:
                items = [item for item in items if item not in self.db[server.id][name]["content"]]
            else:
                self.db[server.id][name]["content"][item] = value
        dataIO.save_json("data/lootbox/servers.json", self.db)
        if items:
            await self.bot.say("{} box has added the following items:\n{}".format(name, "\n".join(items)))
        else:
            await self.bot.say("{} box hasn't added any new items".format(name))

    @edit.command(pass_context=True)
    async def remove(self, ctx, name: str, items: str):
        """Allows removing items to an already created lootbox
           [p]box edit remove "item_1 1, item_2 4, item_3 5"
           Names are fixed when they are added."""
        server = ctx.message.server
        items = items.split(", ")
        itemis = {}
        for item in items:
            item, value = item.split(" ")
            item = item.replace("_", " ").lower()
            itemis[item] = value
        if server.id not in self.db:
            self.db[server.id] = {}
        if name not in self.db[server.id]:
            await self.bot.say("Box doesn't exist, please make sure the spelling is correct and"
                               " that it's found in [p]box list")
            return
        for item in itemis:
            value = itemis[item]
            print(item)
            if item in self.db[server.id][name]["content"]:
                del itemis[item]
                continue
            else:
                self.db[server.id][name]["content"][item] = value
        dataIO.save_json("data/lootbox/servers.json", self.db)
        await self.bot.say("{} box's has added the following items:\n{}".format(name, "\n".join(list(itemis))))

    @box.command(pass_context=True)
    async def info(self, ctx, name: str):
        """Shows info on the box, it's contents
            and the probability of getting an item"""
        name = name.lower()
        server = ctx.message.server
        if server.id not in self.db:
            self.db[server.id] = {}
            dataIO.save_json("data/lootbox/servers.json", self.db)
        if name not in self.db[server.id]:
            await self.bot.say("Please make sure that the name is spelled correctly and "
                               "that you can find it in [p]box list")
            return
        box = list(self.db[server.id][name]["content"].keys())
        values = list(self.db[server.id][name]["content"].values())
        value = sum(values)
        for x in range(len(values)):
            values[x] = values[x]/value
            box[x] = " {:.2%} chance of getting ".format(values[x]) + box[x]
            msg = "You can get the following items from the box:\n"
            msg += "\n".join(box)
        for page in pagify(msg):
            await self.bot.say(page)

    @box.command(pass_context=True)
    async def list(self, ctx):
        """Shows existing boxes in the current server"""
        server = ctx.message.server
        if server.id not in self.db:
            self.db[server.id] = {}
            dataIO.save_json("data/lootbox/servers.json", self.db)
        if len(self.db[server.id]) < 1:
            await self.bot.say("No boxes have been created for this server yet, please create some using [p]box create"
                               " first, thanks")
            return
        boxes = self.db[server.id].keys()
        await self.bot.say("Here are this server's boxes:\n{}".format("\n".join(boxes)))

    @checks.is_owner()
    @box.command(pass_context=True)
    async def remove(self, ctx, name: str):
        """Deletes existing boxes"""
        name = name.lower()
        server = ctx.message.server
        if name not in self.db[server.id]:
            await self.bot.say("Please make sure that the name is spelled correctly and "
                               "that you can find it in [p]box list")
            return
        del self.db[server.id][name]
        dataIO.save_json("data/lootbox/servers.json", self.db)
        await self.bot.say("Box has been removed")

    @box.command(pass_context=True)
    async def sim(self, ctx, name: str, item: str=None):
        """Simulates the opening of a box (It won't be as accurate as an actual lootbox)
           If an item is always in a box, put the item name spelled correctly,
           with capitalization and all
           if you have Key in a box called winter do:
           [p]box sim winter Key"""
        name = name.lower()
        item = item.lower()
        server = ctx.message.server
        if server.id not in self.db:
            self.db[server.id] = {}
        if name not in self.db[server.id]:
            await self.bot.say("Please make sure that the name is spelled correctly and "
                               "that you can find it in [p]box list")
            return
        box = list(self.db[server.id][name]["content"].keys())
        output = self.db[server.id][name]["output"]
        values = list(self.db[server.id][name]["content"].values())
        if item:
            try:
                y = box.index(item)
                del box[y]
                del values[y]
                output = output - 1
            except ValueError:
                item = None
        value = sum(values)
        for x in range(len(values)):
            values[x] = values[x]/value
        meow = numpy.random.choice(box, output, replace=False, p=values)
        if item:
            counter = numpy.random.randint(0, len(meow))
            meow = numpy.insert(meow, counter, item)
            msg = "From {} box you got:\n".format(name)
            msg += "\n".join(meow)
        for page in pagify(msg, delims=["\n"]):
            await self.bot.say(page)


def check_folders():
    # create data/lootbox if not there
    if not os.path.exists('data/lootbox'):
        print('Creating data/lootbox folder...')
        os.mkdir('data/lootbox')


def check_files():
    if not os.path.isfile('data/lootbox/servers.json'):
        print('Creating default lootbox servers.json...')
        # create servers.json if not there
        # put in default values
        default = {}
        dataIO.save_json('data/lootbox/servers.json', default)


def setup(bot):
    check_folders()
    check_files()
    n = Lootbox(bot)
    bot.add_cog(n)
