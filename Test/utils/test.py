import os

from __main__ import send_cmd_help
from .utils import checks
from .utils.chat_formatting import pagify
from .utils.dataIO import dataIO
from discord.ext import commands


class Testy:

    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    pass
