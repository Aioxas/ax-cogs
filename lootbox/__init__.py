from discord.ext import commands
from .lootbox import Lootbox


def setup(bot: commands.Bot):
    n = Lootbox(bot)
    bot.add_cog(n)