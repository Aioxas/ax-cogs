import discord
import numpy

from redbot.core import commands

from redbot.core import Config, checks
from redbot.core.bot import Red


class Trove:

    default_global_settings = {"trovekeeper": [], "troves": {}}

    def __init__(self, bot: Red):
        self.bot = bot
        self._trove = Config.get_conf(self, 4829218492)

    async def permcheck(self, ctx):
        author = ctx.author
        trovekeeper = await self._trove.trovekeeper()
        if author.id != self.bot.settings.owner:
            if author.id not in trovekeeper:
                return False
            else:
                return True
        else:
            return True

    @commands.group()
    async def trove(self, ctx):
        """Trove settings"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help()

    @trove.command(name="add", hidden=True)
    async def add_(self, ctx, name: str, critical: bool, *, cont):
        """If name exists, adds to trove, else creates trove and adds"""
        troves = await self._trove.troves()
        if "[" in cont:
            cont = [cont.strip(r"\" ") for cont in cont[1:-1].split(",")]
        elif "," in cont:
            cont = [cont.strip(r"\" ") for cont in cont.split(",")]
        elif r"\" \"" in cont:
            cont = [cont.strip(r"\" ") for cont in cont.split(r"\" \"")]
        if not self.permcheck(ctx):
            return
        elif not isinstance(critical, bool) or not isinstance(cont, list):
            await ctx.send(
                'Please input the order correctly, i.e., [p]trove add "Spring 2017" True'
                ' ["list","of", "items in trove"]'
            )
            return
        elif len(cont) < 4:
            await ctx.send("Content list is too short, the minimum is 4 items")
            return
        else:
            if name not in troves:
                troves[name] = []
            counti = len(troves[name])
            if counti == 0:
                troves[name].append({"count": 1, "critical": critical, "items": cont})
                await ctx.send("Basket has been initialized, count is now 1")
            for basket in troves[name]:
                if len(set(basket["items"]).intersection(cont)) >= 4:
                    if len(basket["items"]) < 8 and len(set(cont).difference(basket["items"])) > 0:
                        basket["items"].extend(list(set(cont).difference(basket["items"])))
                    basket["count"] += 1
                    await ctx.send(
                        "Count has been updated, basket now has a count of {}".format(
                            basket["count"]
                        )
                    )
                    return
                else:
                    counti -= 1

        await self._trove.troves.set(troves)

    @trove.command()
    async def simulate(self, ctx, *, name):
        """Simulate a trove opening
        Examples:
        >trove simulate Spring 2017
        >trove simulate spring 2017"""
        title = "Treasure Trove"
        logo = "http://www.bns.academy/bot_logo.png"
        trove_normal = "https://cdn.discordapp.com/attachments/302958104084217857/316186037338505216/non-crit.gif"
        trove_critical = (
            "https://cdn.discordapp.com/attachments/302958104084217857/316185272918343680/crit.gif"
        )
        description = "nyan"
        troves = await self._trove.troves()
        trove = [trove for trove in troves.keys()]
        troves2 = [trove.lower() for trove in troves.keys()]
        name = name.lower()
        if name in troves2:
            name = trove[troves2.index(name)]
            plist = troves[name]
        else:
            await ctx.send(
                "Trove not found, please make sure it's spelled correctly."
                "\nYou can check available troves with [p]trove list."
            )
            return
        count = [basket["count"] for basket in plist]
        counti = [counti / sum(count) for counti in count]
        plist = numpy.random.choice(plist, replace=False, p=counti)
        plist_ = plist["items"]
        item_1 = plist_[0]
        item_2 = plist_[1]
        item_3 = plist_[2]
        item_4 = plist_[3]
        item_5 = plist_[4]
        item_6 = plist_[5]
        item_7 = plist_[6]
        item_8 = plist_[7]

        description = (
            ":one: " + item_1 + "\n\n"
            ":two: " + item_2 + "\n\n"
            ":three: " + item_3 + "\n\n"
            ":four: " + item_4 + "\n\n"
            ":five: " + item_5 + "\n\n"
            ":six: " + item_6 + "\n\n"
            ":seven: " + item_7 + "\n\n"
            ":eight: " + item_8
        )

        if plist["critical"] is True:
            image = trove_critical
            colour = 3325695
        else:
            image = trove_normal
            colour = 15844367

        embed = discord.Embed(title=title, description=name, colour=colour)
        embed.set_thumbnail(url=image)
        embed.add_field(name=ctx.author, value=description, inline=True)
        embed.set_footer(text="Blade and Soul Academy", icon_url=logo)
        await ctx.send(embed=embed)

    @trove.command()
    async def list(self, ctx):
        """Lists available troves"""
        troves = await self._trove.troves()
        boxes = troves.keys()
        await ctx.send("Troves available:\n{}".format("\n".join(boxes)))

    @trove.group(hidden=True)
    @checks.is_owner()
    async def keeper(self, ctx):
        """trovekeeper settings"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help()

    @keeper.command(name="add")
    async def __add(self, ctx, name: discord.Member = None):
        """Adds a trovekeeper to the trovekeeping list.
           This allows them to add trove contents"""
        author = ctx.author
        trovekeeper = await self._trove.trovekeeper()
        if name is None:
            name = author
        if name.id in trovekeeper:
            await ctx.send("{} is already registered as a trovekeeper".format(name.display_name))
        else:
            trovekeeper.append(name.id)
        await self._trove.trovekeeper.set(trovekeeper)
        await ctx.send("{} has been registered as a trovekeeper.".format(name.display_name))

    @keeper.command(name="hackadd")
    async def _add(self, ctx, idi: str):
        """Adds a trovekeeper to the trovekeeping list.
           This allows them to add trove contents"""
        author = ctx.author
        trovekeeper = await self._trove.trovekeeper()
        if idi is None:
            name = author # fix this and hackremove, find member object from name
        if idi in trovekeeper:
            await ctx.send("User is already registered as a trovekeeper")
        else:
            trovekeeper.append(idi)
        await self._trove.trovekeeper.set(trovekeeper)
        await ctx.send("{} has been registered as a trovekeeper.".format(name.display_name))

    @keeper.command(name="remove")
    async def __remove(self, ctx, name: discord.Member = None):
        """Removes a trovekeeper from the trovekeeping list"""
        author = ctx.author
        trovekeeper = await self._trove.trovekeeper()
        if name is None:
            name = author
        if len(trovekeeper) < 1:
            await ctx.send(
                "trovekeeper list is currently empty, add new trovekeepers using points keeper add"
                " <Discord name or nickname>"
            )
            return
        if name.id not in trovekeeper:
            await ctx.send(
                "Keeper is not registered, please make sure the name or nickname is correctly spelled. "
                "You can check using points keeper list"
            )
            return
        trovekeeper.remove(name.id)
        await self._trove.trovekeeper.set(trovekeeper)
        await ctx.send("{} has been removed from the trovekeeper list".format(name.display_name))

    @keeper.command(name="hackremove")
    async def _remove(self, ctx, idi: str):
        """Removes a trovekeeper from the trovekeeping list"""
        author = ctx.author
        trovekeeper = await self._trove.trovekeeper()
        if idi is None:
            name = author
        if len(trovekeeper) < 1:
            await ctx.send(
                "trovekeeper list is currently empty, add new trovekeepers using points keeper add"
                " <Discord name or nickname>"
            )
            return
        if idi not in trovekeeper:
            await ctx.send(
                "Keeper is not registered, please make sure the name or nickname is correctly spelled. "
                "You can check using points keeper list"
            )
            return
        trovekeeper.remove(idi)
        await self._trove.trovekeeper.set(trovekeeper)
        await ctx.send("{} has been removed from the trovekeeper list".format(name.display_name))

    @keeper.command(name="list")
    async def __list(self, ctx):
        """Shows the current list of trovekeepers"""
        trovekeeper = await self._trove.trovekeeper()
        if len(trovekeeper) < 1:
            await ctx.send(
                "Trovekeeper list is currently empty, add new trovekeepers using points keeper add"
                " <Discord name or nickname>"
            )
            return
        msg = ""
        for x in trovekeeper:
            trovekeeper[trovekeeper.index(x)] = discord.utils.find(
                lambda N: N.id == x, self.bot.get_all_members()
            ).display_name
        trovekeeper = sorted(
            trovekeeper,
            key=lambda item: (
                int(item.partition(" ")[0]) if item[0].isdigit() else float("inf"),
                item,
            ),
        )
        msg = ", ".join(trovekeeper[:-2] + [" and ".join(trovekeeper[-2:])])
        await ctx.send("Current trovekeepers assigned are: {}".format(msg))
