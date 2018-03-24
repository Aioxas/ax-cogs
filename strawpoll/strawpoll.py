from discord.ext import commands
from cogs.utils.chat_formatting import box
from .utils.dataIO import dataIO
from __main__ import send_cmd_help
import os
import aiohttp
import json


class Strawpoll:

    def __init__(self, bot):
        self.bot = bot
        self.settings = dataIO.load_json("data/strawpoll/strawpoll.json")
        self.fp = "data/strawpoll/strawpoll.json"

    @commands.command(name="results", pass_context=True, no_pm=True)
    async def _results(self, ctx, pollid string):
        """Results of a strawpoll are returned"""
        async with aiohttp.request('GET', 'http://strawpoll.me/api/v2/polls/{}'.format(pollid),
                                       headers={'content-type': 'application/json'}) as resp:
                data = await resp.json()
                s = "{}\n\n".format(html.unescape(data["title"]))
                for o in range(len(data["options"])):
                    s += "{}: {}\n".format(html.unescape(data["options"][o]), data["votes"][o])
                await self.bot.say(box(s))
        
    @commands.command(name="strawpoll", pass_context=True, no_pm=True)
    async def _strawpoll(self, ctx, *, question, options=None):
        """Makes a poll based on questions and choices or options. must be divided by "; "
            Examples:
            [p]strawpoll What is this person?; Who is this person?; Where is this person?; When is this person coming?
            [p]strawpoll What; Who?; Where?; When?; Why?"""
        options_list = question.split('; ')
        title = options_list[0]
        options_list.remove(title)
        if len(options_list) < 2:
            await self.bot.say("You need to specify 2 or more options")
        else:
            normal = {"title": title, "options": options_list}
            request = dict(normal, **self.settings)
            async with aiohttp.request('POST', 'http://strawpoll.me/api/v2/polls',
                                       headers={'content-type': 'application/json'},
                                       data=json.dumps(request)) as resp:
                test = await resp.content.read()
                test = json.loads(test.decode())
                sid = test["id"]
                await self.bot.say("Here's your strawpoll link: http://strawpoll.me/{}".format(sid))

    @commands.group(name="strawpollset", pass_context=True, no_pm=True)
    async def strawpollset(self, ctx):
        """Toggle the different options available for polls
        multi - Whether multiple choice is available
        dupcheck - Whether check for duplicate votes is enforced
        captcha - Whether voters will have to verify captcha"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)
            await self.bot.say("```current settings for the polls are as follows:"
                               "\nmulti: {}\ndupcheck: {}\ncaptcha: {}```"
                               .format(self.settings["multi"], self.settings["dupcheck"], self.settings["captcha"]))

    @strawpollset.command(name="multi", pass_context=True, no_pm=True)
    async def multi(self, ctx):
        """Toggles between True and False values
            True - Multiple choice is available
            False - Multiple choice is not available"""
        if self.settings["multi"] == "true":
            self.settings["multi"] = "false"
            await self.bot.say("Multiple choice no longer available in the poll")
        else:
            self.settings["multi"] = "true"
            await self.bot.say("Multiple choice is now available on the polls.")
        dataIO.save_json(self.fp, self.settings)

    @strawpollset.command(name="dupcheck", pass_context=True, no_pm=True)
    async def dupcheck(self, ctx, option):
        """Toggles between Normal, Permissive, or Disabled values
            Normal - Multiple choice is available
            Permissive - Multiple choice is available
            Disabled - Multiple choice is not available"""
        option = option.lower()
        options = {"normal", "permissive", "disabled"}
        if self.settings["dupcheck"] == option:
            await self.bot.say("Choose another option.")
        elif option not in options:
            await self.bot.say("Choose an actual option.")
        else:
            self.settings["dupcheck"] = option
            if option == "normal":
                await self.bot.say("Dupcheck will now be enforced for duplicate votes.")
            elif option == "permissive":
                await self.bot.say("Dupcheck will now be more lenient on duplicate vote handling.")
            else:
                await self.bot.say("Dupcheck is now disabled.")
            dataIO.save_json(self.fp, self.settings)

    @strawpollset.command(name="captcha", pass_context=True, no_pm=True)
    async def captcha(self, ctx):
        """Toggles between True and False values
            True - Voters will have to do a captcha
            False - Voters will not have to a captcha"""
        if self.settings["captcha"] == "true":
            self.settings["captcha"] = "false"
            await self.bot.say("Voters will no longer have to do a captcha to vote.")
        else:
            self.settings["captcha"] = "true"
            await self.bot.say("Voters will have to do a captcha to vote.")
        dataIO.save_json(self.fp, self.settings)


def check_folders():
    if not os.path.exists("data/strawpoll"):
        print("Creating data/strawpoll folder...")
        os.mkdir("data/strawpoll")


def check_files():
    fp = "data/strawpoll/strawpoll.json"
    if not dataIO.is_valid_json(fp):
        print("Creating strawpoll.json...")
        dataIO.save_json(fp, {"multi": "false", "dupcheck": "normal", "captcha": "false"})


def setup(bot):
    check_folders()
    check_files()
    n = Strawpoll(bot)
    bot.add_cog(n)
