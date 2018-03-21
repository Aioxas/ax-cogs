from .advgoogle import AdvancedGoogle
from discord.ext import commands


def setup(bot: commands.Bot):
    bot.add_cog(AdvancedGoogle(bot))
