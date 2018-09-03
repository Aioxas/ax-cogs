from redbot.core import commands
from .loot import Loot


def setup(bot: commands.Bot):
    bot.add_cog(Loot(bot))
