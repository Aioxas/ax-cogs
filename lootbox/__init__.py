from redbot.core import commands
from .lootbox import Lootbox


def setup(bot: commands.Bot):
    bot.add_cog(Lootbox(bot))
