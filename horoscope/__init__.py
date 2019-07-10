from redbot.core import commands, data_manager
from .horoscope import Horoscope


def setup(bot: commands.Bot):
    n = Horoscope(bot)
    data_manager.bundled_data_path(n)
    bot.add_cog(n)
