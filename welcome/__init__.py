from discord.ext import commands
from .welcome import Welcome


def setup(bot: commands.Bot):
    n = Welcome(bot)
    bot.add_cog(n)