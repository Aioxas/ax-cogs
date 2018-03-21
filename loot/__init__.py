from discord.ext import commands
from .loot import Loot


def setup(bot: commands.Bot):
    n = Loot(bot)
    bot.add_cog(n)