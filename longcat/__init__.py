from redbot.core import commands
from .longcat import Longcat


def setup(bot: commands.Bot):
    cog = Longcat(bot)
    bot.add_cog(cog)
