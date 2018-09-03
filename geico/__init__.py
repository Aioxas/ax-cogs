from redbot.core import commands
from .geico import Geico


def setup(bot: commands.Bot):
    bot.add_cog(Geico(bot))
