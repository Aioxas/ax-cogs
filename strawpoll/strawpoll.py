from redbot.core import Config, commands
import aiohttp
import json
import html
from redbot.core.utils.chat_formatting import box

from redbot.core.bot import Red


class Strawpoll:

    default_guild_settings = {"multi": "false", "dupcheck": "normal", "captcha": "false"}

    def __init__(self, bot: Red):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=self.bot.loop)
        self.url = "https://www.strawpoll.me/api/v2"
        self._strawpoll = Config.get_conf(self, 4285208923)

        self._strawpoll.register_guild(**self.default_guild_settings)

    def __unload(self):
        self.session.close()

    @commands.guild_only()
    @commands.command(name="results")
    async def _results(self, ctx, pollid):
        """Results of a strawpoll are returned"""
        async with self.session.get(
            self.url + "/polls/{}".format(pollid), headers={"content-type": "application/json"}
        ) as resp:
            data = await resp.json()
            s = "{}\n\n".format(html.unescape(data["title"]))
            for o in range(len(data["options"])):
                s += "{}: {}\n".format(html.unescape(data["options"][o]), data["votes"][o])
            await ctx.send(box(s))

    @commands.guild_only()
    @commands.command(name="strawpoll")
    async def strawpoll(self, ctx, *, question, options=None):
        """Makes a poll based on questions and choices or options. must be divided by "; "
            Examples:
            [p]strawpoll What is this person?; Who is this person?; Where is this person?; When is this person coming?
            [p]strawpoll What; Who?; Where?; When?; Why?"""
        settings = await self._strawpoll.guild(ctx.guild).all()
        options_list = question.split("; ")
        title = options_list[0]
        options_list.remove(title)
        if len(options_list) < 2:
            await ctx.send("You need to specify 2 or more options")
        else:
            normal = {"title": title, "options": options_list}
            request = dict(normal, **settings)
            async with self.session.post(
                self.url + "/polls",
                headers={"content-type": "application/json"},
                data=json.dumps(request),
            ) as resp:
                test = await resp.content.read()
                test = json.loads(test.decode())
                sid = test["id"]
                await ctx.send("Here's your strawpoll link: http://strawpoll.me/{}".format(sid))

    @commands.guild_only()
    @commands.group(name="strawpollset")
    async def strawpollset(self, ctx):
        """Toggle the different options available for polls
        multi - Whether multiple choice is available
        dupcheck - Whether check for duplicate votes is enforced
        captcha - Whether voters will have to verify captcha"""
        settings = await self._strawpoll.guild(ctx.guild).all()
        if ctx.invoked_subcommand is None:
            await ctx.send_help()
            await ctx.send(
                "```current settings for the polls are as follows:"
                "\nmulti: {}\ndupcheck: {}\ncaptcha: {}```".format(
                    settings["multi"], settings["dupcheck"], settings["captcha"]
                )
            )

    @strawpollset.command(name="multi")
    async def multi(self, ctx):
        """Toggles between True and False values
            True - Multiple choice is available
            False - Multiple choice is not available"""
        settings = await self._strawpoll.guild(ctx.guild).all()
        if settings["multi"] == "true":
            settings["multi"] = "false"
            await ctx.send("Multiple choice no longer available in the poll")
        else:
            settings["multi"] = "true"
            await ctx.send("Multiple choice is now available on the polls.")
        await self.save_db(ctx, settings)

    @strawpollset.command(name="dupcheck")
    async def dupcheck(self, ctx, option):
        """Toggles between Normal, Permissive, or Disabled values
            Normal - Multiple choice is available
            Permissive - Multiple choice is available
            Disabled - Multiple choice is not available"""
        option = option.lower()
        options = {"normal", "permissive", "disabled"}
        settings = await self._strawpoll.guild(ctx.guild).all()
        if settings["dupcheck"] == option:
            await ctx.send("Choose another option.")
        elif option not in options:
            await ctx.send("Choose an actual option.")
        else:
            settings["dupcheck"] = option
            if option == "normal":
                await ctx.send("Dupcheck will now be enforced for duplicate votes.")
            elif option == "permissive":
                await ctx.send("Dupcheck will now be more lenient on duplicate vote handling.")
            else:
                await ctx.send("Dupcheck is now disabled.")
            await self.save_db(ctx, settings)

    @strawpollset.command(name="captcha")
    async def captcha(self, ctx):
        """Toggles between True and False values
            True - Voters will have to do a captcha
            False - Voters will not have to a captcha"""
        settings = await self._strawpoll.guild(ctx.guild).all()
        if settings["captcha"] == "true":
            settings["captcha"] = "false"
            await ctx.send("Voters will no longer have to do a captcha to vote.")
        else:
            settings["captcha"] = "true"
            await ctx.send("Voters will have to do a captcha to vote.")
        await self.save_db(ctx, settings)

    async def save_db(self, ctx, settings: dict):
        await self._strawpoll.guild(ctx.guild).set(settings)
