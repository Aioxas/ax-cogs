from redbot.core import commands
from .strawpoll import Strawpoll


def setup(bot: commands.Bot):
    bot.add_cog(Strawpoll(bot))
