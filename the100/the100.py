import aiohttp
import asyncio
import os

from discord.ext import commands
from cogs.utils.dataIO import dataIO
from __main__ import send_cmd_help
from cogs.utils import checks
from cogs.utils.chat_formatting import box


class The100:
    """meow"""

    def __init__(self, bot):
        self.bot = bot
        self.path = "data/the100"
        self.json = self.path + "/db.json"
        self.db = dataIO.load_json(self.json)
        self.session = aiohttp.ClientSession(loop=bot.loop)
        self.headers = {"Authorization": "Token token=\"{}\"", "content-type": "application/json"}

    def permcheck(self, ctx):
        author = ctx.message.author
        server = ctx.message.server
        if server.id not in self.db:
            self.db[server.id] = {"token": None, "role": None}
            dataIO.save_json(self.json, self.db)
            return False
        if "role" in self.db[server.id]:
            role = self.db[server.id]["role"]
        else:
            self.db[server.id]["role"] = None
            dataIO.save_json(self.json, self.db)
            return False
        if author.id != self.bot.settings.owner \
                or author.id != server.owner.id:
            return role in [r.name.lower() for r in author.roles]
        else:
            return True

    @commands.group(pass_context=True)
    async def the100(self, ctx):
        """The100 settingS"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)
        elif not self.permcheck(ctx):
            return

    @the100.command(pass_context=True)
    async def group(self, ctx, name: str):
        """Searches for a group based on ID.
           How-to ID:
           https://www.the100.io/groups/4311
           https://www.the100.io/groups/X
           Where X is the Group ID"""
        server = ctx.message.server
        url = "https://www.the100.io/api/v1/groups/{}".format(name)
        if not self.permcheck(ctx):
            return
        if self.db[server.id]["token"]:
            self.headers["Authorization"] = self.headers["Authorization"].format(self.db[server.id]["token"])
            headers = self.headers
        else:
            await self.bot.say("Token has not been set, please set it using [p]the100 set token in a pm")
            return
        async with self.session.get(url, headers=headers) as resp:
            response = await resp.json()
        msg = response["name"]
        await self.bot.say("Group name: {}".format(msg))

    @the100.command(pass_context=True)
    async def users(self, ctx, name: str):
        """Shows the users belonging to a group based on ID.
           How-to ID:
           https://www.the100.io/groups/4311
           https://www.the100.io/groups/X
           Where X is the Group ID"""
        server = ctx.message.server
        url = "https://www.the100.io/api/v1/groups/{}/users".format(name)
        if not self.permcheck(ctx):
            return
        if self.db[server.id]["token"]:
            self.headers["Authorization"] = self.headers["Authorization"].format(self.db[server.id]["token"])
            headers = self.headers
        else:
            await self.bot.say("Token has not been set, please set it using [p]the100 set token in a pm")
            return
        async with self.session.get(url, headers=headers) as resp:
            response = await resp.json()
        msg = [response["gamertag"] for response in response]
        msg = ", ".join(msg[:-2] + [" and ".join(msg[-2:])])
        await self.bot.say("Users in group: {}".format(msg))

    @the100.command(pass_context=True)
    async def games(self, ctx, name: str):
        """Shows game sessions for a group based on ID.
           How-to ID:
           https://www.the100.io/groups/4311
           https://www.the100.io/groups/X
           Where X is the Group ID"""
        server = ctx.message.server
        url = "https://www.the100.io/api/v1/groups/{}/gaming_sessions".format(name)
        if not self.permcheck(ctx):
            return
        if self.db[server.id]["token"]:
            self.headers["Authorization"] = self.headers["Authorization"].format(self.db[server.id]["token"])
            headers = self.headers
        else:
            await self.bot.say("Token has not been set, please set it using this command in a PM, [p]the100 set token")
            return
        async with self.session.get(url, headers=headers) as resp:
            response = await resp.json()
        msg = ""
        for s, x in enumerate(response, start=1):
            for y in ["category", "team_size", "time_zone",
                      "group_only", "party_size", "light_level", "platform_formatted",
                      "start_time", "has_spots_open", "confirmed_sessions"]:
                if y == "confirmed_sessions":
                    users = [z["user"]["gamertag"] for z in x[y]]
                    msg += "Users: " + ", ".join(users[:-2] + [" and ".join(users[-2:])]) + "\n"
                elif y == "start_time":
                    time = "".join(str(x[y]).rsplit(":", 1))
                    msg += "Start time: " + " ".join((time[:-9] + " " + time[-5:]).split("T")) + "\n"
                elif y == "platform_formatted":
                    msg += "Platform: " + x[y] + "\n"

                else:
                    if "_" in y:
                        m = [a[0].upper()+a[1:] for a in y.split("_")]
                        msg += " ".join(m) + ": " + str(x[y]) + "\n"
                    else:
                        msg += y[0].upper() + y[1:] + ": " + str(x[y]) + "\n"
            await self.bot.say("Event Info #{}:\n{}".format(s, box(msg)))
            await asyncio.sleep(2)

    @the100.command(pass_context=True)
    async def statuses(self, ctx, name: str):
        """Shows statuses of players in a group based on ID.
           How-to ID:
           https://www.the100.io/groups/4311
           https://www.the100.io/groups/X
           Where X is the Group ID"""
        server = ctx.message.server
        url = "https://www.the100.io/api/v1/groups/{}/statuses".format(name)
        if not self.permcheck(ctx):
            return
        if self.db[server.id]["token"]:
            self.headers["Authorization"] = self.headers["Authorization"].format(self.db[server.id]["token"])
            headers = self.headers
        else:
            await self.bot.say("Token has not been set, please set it using [p]the100 set token in a pm")
            return
        async with self.session.get(url, headers=headers) as resp:
            response = await resp.json()
        msg = "No one has set a status yet. Please try again later." if response == [] else response
        await self.bot.say("{}".format(msg))

    @the100.group(pass_context=True)
    @checks.serverowner()
    async def set(self, ctx):
        """Settings"""
        if ctx.invoked_subcommand is None or \
                isinstance(ctx.invoked_subcommand, commands.Group):
            server = ctx.message.server
            await send_cmd_help(ctx)
            await self.bot.say("Token: {}\nRole: {}```"
                               .format("Set" if self.db[server.id]["token"] else "Not Set",
                                       self.db[server.id]["role"]))

    @set.command(pass_context=True)
    async def token(self, ctx, token: str):
        """Allows you to set the API Token for retrieving information.
           Warning, please do this through PM with the bot.
           Another way is to create a channel that only the bot and you can access."""
        server = ctx.message.server
        if server.id not in self.db:
            self.db[server.id] = {"token": None, "role": None}
        else:
            if self.db[server.id]["token"]:
                await self.bot.say("Are you sure you want to overwrite the current token? Yes/No")
                answer = await self.bot.wait_for_message(timeout=15,
                                                         author=ctx.message.author)
                if answer is None:
                    await self.bot.say("Action cancelled")
                elif answer.content.lower().strip() == "yes":
                    self.db[server.id]["token"] = token
                    await self.bot.say("Token overwritten")
                    dataIO.save_json(self.json, self.db)
                else:
                    await self.bot.say("Action cancelled")
                return
            else:
                self.db[server.id]["token"] = token
        dataIO.save_json(self.json, self.db)
        await self.bot.say("Token successfully set")

    @set.command(pass_context=True)
    async def role(self, ctx, *, role: str):
        """Allows you to set the role that will have access to the command.
           If a role has spaces, just write it as is.
           Examples:
           the100 set role man gler
           the100 set role barbell"""
        role = role.lower()
        server = ctx.message.server
        if server.id not in self.db:
            self.db[server.id] = {"token": None, "role": None}
        else:
            if self.db[server.id]["role"]:
                await self.bot.say("Are you sure you want to overwrite the current access role? Yes/No")
                answer = await self.bot.wait_for_message(timeout=15,
                                                         author=ctx.message.author)
                if answer is None:
                    await self.bot.say("Action cancelled")
                elif answer.content.lower().strip() == "yes":
                    self.db[server.id]["role"] = role
                    await self.bot.say("role overwritten")
                    dataIO.save_json(self.json, self.db)
                else:
                    await self.bot.say("Action cancelled")
                return
            else:
                self.db[server.id]["role"] = role
        dataIO.save_json(self.json, self.db)
        await self.bot.say("Access role {} has been set".format(role))


def check_folders():
    f = "data/the100"
    if not os.path.exists(f):
        print("creating data/the100 directory")
        os.mkdir(f)


def check_files():
    f = 'data/the100/db.json'
    if not os.path.isfile(f):
        default = {}
        print('Creating default the100/db.json...')
        dataIO.save_json(f, default)


def setup(bot):
    check_folders()
    check_files()
    bot.add_cog(The100(bot))
