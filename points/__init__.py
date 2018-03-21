from discord.ext import commands
from .points import Points


def setup(bot: commands.Bot):
    n = Points(bot)
    bot.add_cog(n)