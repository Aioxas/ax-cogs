from redbot.core import commands
from .points import Points


def setup(bot: commands.Bot):
    bot.add_cog(Points(bot))
