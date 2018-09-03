from .advgoogle import AdvancedGoogle
from redbot.core import commands


def setup(bot: commands.Bot):
    bot.add_cog(AdvancedGoogle(bot))
