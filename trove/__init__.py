from discord.ext import commands
from .trove import Trove


def setup(bot: commands.Bot):
    n = Trove(bot)
    bot.add_cog(n)