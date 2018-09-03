from redbot.core import commands
from .the100 import The100


def setup(bot: commands.Bot):
    bot.add_cog(The100(bot))
