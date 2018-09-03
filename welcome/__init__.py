from redbot.core import commands
from .welcome import Welcome


def setup(bot: commands.Bot):
    bot.add_cog(Welcome(bot))
