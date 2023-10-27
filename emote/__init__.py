from redbot.core import commands
from .emote import Emote

__red_end_user_data_statement__ = "This cog does not persistently store data or metadata about users."


async def setup(bot: commands.Bot):
    n = Emote(bot)
    await bot.add_cog(n)
