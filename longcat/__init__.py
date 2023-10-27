from redbot.core import commands
from .longcat import Longcat

__red_end_user_data_statement__ = "This cog does not persistently store data or metadata about users."


async def setup(bot: commands.Bot):
    cog = Longcat(bot)
    await bot.add_cog(cog)
