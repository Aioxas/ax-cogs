import discord
import os

from .utils import checks
from .utils.dataIO import dataIO
from __main__ import send_cmd_help
from discord.ext import commands


class Loot:

    def __init__(self, bot):
        self.bot = bot
        self.db = dataIO.load_json("data/loot/servers.json")

    @commands.group(pass_context=True)
    async def loot(self, ctx):
        """Loot related commands"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @loot.command(pass_context=True)
    async def add(self, ctx, name: str, char: str, price: int):
        """Adds players and amounts paid to an item"""
        name = name.lower()
        server = ctx.message.server
        if server.id not in self.db:
            self.db[server.id] = {}
        if name not in self.db[server.id]:
            await self.bot.say("item doesn't exist, please use [p]loot create first")
            return
        self.db[server.id][name][char] = price
        dataIO.save_json("data/loot/servers.json", self.db)
        await self.bot.say("{} paid {} for {}".format(char, price, name))

    @loot.command(pass_context=True)
    async def create(self, ctx, name: str):
        """Creates an item in the current server."""
        name = name.lower()
        server = ctx.message.server
        if server.id not in self.db:
            self.db[server.id] = {}
        if name in self.db[server.id]:
            await self.bot.say("Item already exists, use another name.")
            return
        self.db[server.id][name] = {}
        dataIO.save_json("data/loot/servers.json", self.db)
        await self.bot.say("{} has been added.".format(name))

    @loot.command(pass_context=True)
    async def info(self, ctx, name: str):
        """Shows who has invested in the item"""
        name = name.lower()
        server = ctx.message.server
        if server.id not in self.db:
            self.db[server.id] = {}
            dataIO.save_json("data/loot/servers.json", self.db)
        if name not in self.db[server.id]:
            await self.bot.say("Please make sure that the name is spelled correctly and "
                               "that you can find it in [p]loot list")
            return
        players = "\n".join(list(self.db[server.id][name].keys()))
        gold = "\n".join(str(x) for x in list(self.db[server.id][name].values()))
        embed = discord.Embed(color=6465603)
        embed.set_author(name=name)
        embed.add_field(name="__Players__", value=players)
        embed.add_field(name="__Price Paid__", value=gold)
        await self.bot.say(embed=embed)

    @loot.command(pass_context=True)
    async def list(self, ctx):
        """Shows existing loot in the current server"""
        server = ctx.message.server
        if server.id not in self.db:
            self.db[server.id] = {}
            dataIO.save_json("data/loot/servers.json", self.db)
        if len(self.db[server.id]) < 1:
            await self.bot.say("No items have been created for this server yet, please create some using [p]item create"
                               " first, thanks")
            return
        items = self.db[server.id].keys()
        await self.bot.say("Here are this server's items:\n{}".format("\n".join(items)))

    @checks.is_owner()
    @loot.command(pass_context=True)
    async def remove(self, ctx, name: str, char: str=None):
        """Deletes existing characters in an item or items"""
        name = name.lower()
        server = ctx.message.server
        if name not in self.db[server.id]:
            await self.bot.say("Please make sure that the name is spelled correctly and "
                               "that you can find it in [p]loot list")
            return
        if char is None:
            del self.db[server.id][name]
        elif char in self.db[server.id][name]:
            del self.db[server.id][name][char]
        dataIO.save_json("data/loot/servers.json", self.db)
        await self.bot.say("{} has been removed".format(char or name))


def check_folders():
    # create data/loot if not there
    if not os.path.exists('data/loot'):
        print('Creating data/loot folder...')
        os.mkdir('data/loot')


def check_files():
    if not os.path.isfile('data/loot/servers.json'):
        print('Creating default loot servers.json...')
        # create servers.json if not there
        # put in default values
        default = {}
        dataIO.save_json('data/loot/servers.json', default)


def setup(bot):
    check_folders()
    check_files()
    n = Loot(bot)
    bot.add_cog(n)