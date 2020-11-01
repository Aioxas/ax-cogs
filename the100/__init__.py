from redbot.core import commands
from .the100 import The100

__red_end_user_data_statement__ = (
    "This cog does not store user-specific data."
)


def setup(bot: commands.Bot):
    bot.add_cog(The100(bot))
