import numpy
import discord

from discord.ext import commands

from redbot.core import Config, checks
from redbot.core.bot import Red


class Lootbox:

    default_guild_settings = {
        "boxes": {}
    }

    def __init__(self, bot: Red):
        self.bot = bot
        self._lootbox = Config.get_conf(self, 2184719022)

        self._lootbox.register_guild(**self.default_guild_settings)

    @commands.group(pass_context=True)
    async def box(self, ctx):
        """Box related commands"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help()

    @box.command(pass_context=True)
    async def add(self, ctx, name: str, content: str, multi: int=None):
        """Adds items to a box
           Usage:
           winter = box name
           [p]box add winter Key 20
           [p]box add winter "Key, Unsealing Charm" 20"""
        name = name.lower()
        guild = ctx.guild
        boxes = await self._lootbox.guild(guild).boxes()
        counter = 0
        if name not in boxes:
            await ctx.send("Box doesn't exist, please use [p]box create first")
            return
        if ", " in content:
            content = content.split(", ")
        elif "," in content:
            content = content.split(",")
        if multi and type(content) is not list:
            content = [content.lower()] * multi
        else:
            content = content * multi
        for x in content:
            x = x.lower()
            if x in boxes[name]["content"]:
                boxes[name]["content"][x] += 1
            else:
                counter += 1
                continue
        await ctx.send("Items added to {} box: {}. Items failed to add: "
                       "{}".format(name, len(content) - counter, counter))
        await self._lootbox.guild(guild).boxes.set(boxes)

    @box.command(pass_context=True)
    async def create(self, ctx, name: str, output: int, *, content: str):
        """Creates a box in the current server
           [p]box create winter 6 Key, Unsealing Charm, Black Padded Coat, Infernal Horn"""
        name = name.lower()
        guild = ctx.guild
        boxes = await self._lootbox.guild(guild).boxes()
        if name in boxes:
            await ctx.send("Box already exists, please use another name or use box edit to change the contents")
            return
        if ", " in content:
            content = content.split(", ")
        elif "," in content:
            content = content.split(",")
        boxes[name] = {"content": {}, "output": output}
        for x in content:
            x = x.lower()
            boxes[name]["content"][x] = 0
        await ctx.send("{} box has been added, it has {} items and outputs {}"
                       " items".format(name, len(content), output))
        await self._lootbox.guild(guild).boxes.set(boxes)

    @checks.mod_or_permissions()
    @box.group(pass_context=True)
    async def edit(self, ctx):
        """Allows editing of box names or output"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help()

    @edit.command(pass_context=True)
    async def name(self, ctx, name: str, newname: str):
        """Allows editing of the boxes' name
           winter = current name
           autumn = new name
           [p]box edit name winter autumn"""
        name = name.lower()
        newname = newname.lower()
        guild = ctx.guild
        boxes = await self._lootbox.guild(guild).boxes()
        if newname in boxes:
            await ctx.send("Box already exists, please use another name")
            return
        if name not in boxes:
            await ctx.send("Box doesn't exist, please make sure the spelling is correct and"
                           " that it's found in [p]box list")
            return
        boxes[newname] = boxes.pop(name, None)
        await ctx.send("{} has been renamed to {}".format(name, newname))
        await self._lootbox.guild(guild).boxes.set(boxes)

    @edit.command(pass_context=True)
    async def output(self, ctx, name: str, output: int):
        """Allows adjusting how many items
           come out of the simulated lootbox
           [p]box edit output 20"""
        guild = ctx.guild
        boxes = await self._lootbox.guild(guild).boxes()
        if name not in boxes:
            await ctx.send("Box doesn't exist, please make sure the spelling is correct and"
                           " that it's found in [p]box list")
            return
        boxes[name]["output"] = output
        await ctx.send("{} box's output has changed to {}".format(name, output))
        await self._lootbox.guild(guild).boxes.set(boxes)

    @box.command(pass_context=True)
    async def info(self, ctx, name: str):
        """Shows info on the box, it's contents
            and the probability of getting an item"""
        name = name.lower()
        guild = ctx.guild
        boxes = await self._lootbox.guild(guild).boxes()
        if name not in boxes:
            await ctx.send("Please make sure that the name is spelled correctly and "
                           "that you can find it in [p]box list")
            return

        outputs = {}
        value = sum(list(boxes[name]["content"].values()))
        pagenum = 0  # alternatively if you dont want this counter, check the length of everything in the str to make sure its less than your limit, same deal with charcount
        outputs[pagenum] = []
        charcount = 0  # if for embeds, make sure this doesnt exceed 1024, for regular text then 2k
        box = boxes[name]["content"]
        for x in box:  # this for loop goes through the dict, x is the key
            s = " {:.8%} chance of getting {}".format(box[x] / value, x)  # this is what each line will say, whatever item has that chance
            charcount += len(s)
            if charcount <= 900:  # change to 2k if you arent doing embed fields
                outputs[pagenum].append(s)
            else:
                charcount = 0
                pagenum += 1
                outputs[pagenum] = []
                outputs[pagenum].append(s)

        embed = discord.Embed()
        embed.title = name
        for i in outputs:
            embed.add_field(name="Set {}".format(i + 1), value=str(outputs[i])[1:-1].replace(" '", "").replace("'", "").replace(',', '\n'))

        await ctx.send(embed=embed)

    @box.command(pass_context=True)
    async def list(self, ctx):
        """Shows existing boxes in the current server"""
        guild = ctx.guild
        boxes = await self._lootbox.guild(guild).boxes()
        if len(boxes) < 1:
            await ctx.send("No boxes have been created for this server yet, please create some using [p]box create"
                           " first, thanks")
            return
        boxes = boxes.keys()
        await ctx.send("Here are this server's boxes:\n{}".format("\n".join(boxes)))

    @checks.is_owner()
    @box.command(pass_context=True)
    async def remove(self, ctx, name: str):
        """Deletes existing boxes"""
        name = name.lower()
        guild = ctx.guild
        boxes = await self._lootbox.guild(guild).boxes()
        if name not in boxes:
            await ctx.send("Please make sure that the name is spelled correctly and "
                           "that you can find it in [p]box list")
            return
        boxes.pop(name, None)
        await self._lootbox.guild(guild).boxes.set(boxes)
        await ctx.send("Box has been removed")

    @box.command(pass_context=True)
    async def sim(self, ctx, name: str, item: str=None):
        """Simulates the opening of a box (It won't be as accurate as an actual lootbox)
           If an item is always in a box, put the item name spelled correctly,
           with capitalization and all
           if you have Key in a box called winter do:
           [p]box sim winter Key"""
        name = name.lower()
        if item is not None:
            item = item.lower()
        guild = ctx.guild
        boxes = await self._lootbox.guild(guild).boxes()
        if name not in boxes:
            await ctx.send("Please make sure that the name is spelled correctly and "
                           "that you can find it in [p]box list")
            return
        box = list(boxes[name]["content"].keys())
        output = boxes[name]["output"]
        values = list(boxes[name]["content"].values())
        if item:
            try:
                y = box.index(item)
                del box[y]
                del values[y]
                output = output - 1
            except ValueError:
                item = None
        value = sum(values)
        if sum(values) == 0:
            ctx.send("add some items to your box first usin [p]box add <name> <content> <multi>")
            return
        for x in range(len(values)):
            values[x] = values[x] / value
        meow = numpy.random.choice(box, output, replace=False, p=values)
        if item:
            counter = numpy.random.randint(0, len(meow))
            meow = numpy.insert(meow, counter, item)
        await ctx.send("From {} box you got:\n{}".format(name, "\n".join(meow)))
