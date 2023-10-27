from redbot.core import commands
from .points import Points

__red_end_user_data_statement__ = "This cog does not persistently store data or metadata about users."


async def setup(bot: commands.Bot):
    await bot.add_cog(Points(bot))
