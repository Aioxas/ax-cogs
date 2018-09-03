import aiohttp
import asyncio
import os

from redbot.core import checks, commands, Config
from redbot.core.utils.chat_formatting import box
from redbot.core.bot import Red


class The100:

    default_guild_settings = {"token": None, "role": None}

    def __init__(self, bot: Red):
        self.bot = bot
        self._the100 = Config.get_conf(self, 4879596100)
        self.session = aiohttp.ClientSession(loop=self.bot.loop)
        self.headers = {"Authorization": 'Token token="{}"', "content-type": "application/json"}
        self.url = "https://www.the100.io/api/v1/groups"
        self._the100.register_guild(**self.default_guild_settings)

    def __unload(self):
        self.session.close()

    async def permcheck(self, ctx):
        author = ctx.message.author
        guild = ctx.message.guild
        data = await self._the100.guild(ctx.guild).all()
        if "role" in data:
            role = data["role"]
        else:
            data["role"] = None
            await self._the100.guild(ctx.guild).set(data)
            return False
        if author.id != self.bot.settings.owner or author.id != guild.owner.id:
            if role not in [r.name.lower() for r in author.roles]:
                return False
            else:
                return True
        else:
            return True

    @commands.group()
    async def the100(self, ctx):
        """The100 settingS"""
        if ctx.invoked_subcommand is None:
            await ctx.send_cmd_help()
        elif not (await self.permcheck(ctx)):
            return

    @the100.command()
    async def group(self, ctx, name: str):
        """Searches for a group based on ID.
           How-to ID:
           https://www.the100.io/groups/4311
           https://www.the100.io/groups/X
           Where X is the Group ID"""
        url = self.url + "/{}".format(name)
        data = await self._the100.guild(ctx.guild).all()
        if not self.permcheck(ctx):
            return
        if data["token"]:
            self.headers["Authorization"] = self.headers["Authorization"].format(data["token"])
            headers = self.headers
        else:
            await ctx.send(
                "Token has not been set, please set it using [p]the100 set token in a pm"
            )
            return
        async with self.session.get(url, headers=headers) as resp:
            response = await resp.json()
        msg = response["name"]
        await ctx.send("Group name: {}".format(msg))

    @the100.command()
    async def users(self, ctx, name: str):
        """Shows the users belonging to a group based on ID.
           How-to ID:
           https://www.the100.io/groups/4311
           https://www.the100.io/groups/X
           Where X is the Group ID"""
        url = self.url + "/{}/users".format(name)
        data = await self._the100.guild(ctx.guild).all()
        if not self.permcheck(ctx):
            return
        if data["token"]:
            self.headers["Authorization"] = self.headers["Authorization"].format(data["token"])
            headers = self.headers
        else:
            await ctx.send(
                "Token has not been set, please set it using [p]the100 set token in a pm"
            )
            return
        async with self.session.get(url, headers=headers) as resp:
            response = await resp.json()
        msg = [response["gamertag"] for response in response]
        msg = ", ".join(msg[:-2] + [" and ".join(msg[-2:])])
        await ctx.send("Users in group: {}".format(msg))

    @the100.command()
    async def games(self, ctx, name: str):
        """Shows game sessions for a group based on ID.
           How-to ID:
           https://www.the100.io/groups/4311
           https://www.the100.io/groups/X
           Where X is the Group ID"""
        url = self.url + "/{}/gaming_sessions".format(name)
        data = await self._the100.guild(ctx.guild).all()
        if not self.permcheck(ctx):
            return
        if data["token"]:
            self.headers["Authorization"] = self.headers["Authorization"].format(data["token"])
            headers = self.headers
        else:
            await ctx.send(
                "Token has not been set, please set it using this command in a PM, [p]the100 set token"
            )
            return
        async with self.session.get(url, headers=headers) as resp:
            response = await resp.json()
        msg = ""
        for s, x in enumerate(response, start=1):
            for y in [
                "category",
                "team_size",
                "time_zone",
                "group_only",
                "party_size",
                "light_level",
                "platform_formatted",
                "start_time",
                "has_spots_open",
                "confirmed_sessions",
            ]:
                if y == "confirmed_sessions":
                    users = []
                    for z in x[y]:
                        users.append(z["user"]["gamertag"])
                    msg += "Users: " + ", ".join(users[:-2] + [" and ".join(users[-2:])]) + "\n"
                elif y == "start_time":
                    time = "".join(str(x[y]).rsplit(":", 1))
                    msg += (
                        "Start time: " + " ".join((time[:-9] + " " + time[-5:]).split("T")) + "\n"
                    )
                elif y == "platform_formatted":
                    msg += "Platform: " + x[y] + "\n"

                else:
                    if "_" in y:
                        m = [a[0].upper() + a[1:] for a in y.split("_")]
                        msg += " ".join(m) + ": " + str(x[y]) + "\n"
                    else:
                        msg += y[0].upper() + y[1:] + ": " + str(x[y]) + "\n"
            await ctx.send("Event Info #{}:\n{}".format(s, box(msg)))
            await asyncio.sleep(2)

    @the100.command()
    async def statuses(self, ctx, name: str):
        """Shows statuses of players in a group based on ID.
           How-to ID:
           https://www.the100.io/groups/4311
           https://www.the100.io/groups/X
           Where X is the Group ID"""
        url = self.url + "/{}/statuses".format(name)
        data = await self._the100.guild(ctx.guild).all()
        if not self.permcheck(ctx):
            return
        if data["token"]:
            self.headers["Authorization"] = self.headers["Authorization"].format(data["token"])
            headers = self.headers
        else:
            await ctx.send(
                "Token has not been set, please set it using [p]the100 set token in a pm"
            )
            return
        async with self.session.get(url, headers=headers) as resp:
            response = await resp.json()
        msg = (
            "No one has set a status yet. Please try again later." if response == [] else response
        )
        await ctx.send("{}".format(msg))

    @the100.group()
    @checks.guildowner()
    async def the100set(self, ctx):
        """Settings"""
        data = await self._the100.guild(ctx.guild).all()
        if ctx.invoked_subcommand is None or isinstance(ctx.invoked_subcommand, commands.Group):
            await ctx.send_cmd_help()
            await ctx.send(
                "Token: {}\nRole: {}```".format(
                    "Set" if data["token"] else "Not Set", data["role"]
                )
            )

    @the100set.command()
    async def token(self, ctx, token: str):
        """Allows you to set the API Token for retrieving information.
           Warning, please do this through PM with the bot.
           Another way is to create a channel that only the bot and you can access."""
        author = ctx.message.author
        data = await self._the100.guild(ctx.guild).all()
        if data["token"]:

            def check(m):
                return author == m.author

            await ctx.send("Are you sure you want to overwrite the current token? Yes/No")
            answer = await self.bot.wait_for("message", timeout=15, check=check)
            if answer is None:
                await ctx.send("Action cancelled")
                return
            elif answer.content.lower().strip() == "yes":
                data["token"] = token
                await ctx.send("Token overwritten")
                await self._the100.guild(ctx.guild).set(data)
                return
            else:
                await ctx.send("Action cancelled")
                return
        else:
            data["token"] = token
        await self._the100.guild(ctx.guild).set(data)
        await ctx.send("Token successfully set")

    @the100set.command()
    async def role(self, ctx, *, role: str):
        """Allows you to set the role that will have access to the command.
           If a role has spaces, just write it as is.
           Examples:
           the100 set role man gler
           the100 set role barbell"""
        role = role.lower()
        author = ctx.message.author
        data = await self._the100.guild(ctx.guild).all()
        if data["role"]:

            def check(m):
                return author == m.author

            await ctx.send("Are you sure you want to overwrite the current access role? Yes/No")
            answer = await self.bot.wait_for("message", timeout=15, check=check)
            if answer is None:
                await ctx.send("Action cancelled")
                return
            elif answer.content.lower().strip() == "yes":
                data["role"] = role
                await ctx.send("role overwritten")
                await self._the100.guild(ctx.guild).set(data)
                return
            else:
                await ctx.send("Action cancelled")
                return
        else:
            data["role"] = role
        await self._the100.guild(ctx.guild).set(data)
        await ctx.send("Access role {} has been set".format(role))
