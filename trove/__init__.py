from redbot.core import commands
from .trove import Trove


def setup(bot: commands.Bot):
    bot.add_cog(Trove(bot))
