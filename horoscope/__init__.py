from redbot.core import commands, data_manager
from .horoscope import Horoscope


def setup(bot: commands.Bot):
    n = Horoscope(bot)
    data_manager.load_bundled_data(n, __file__)
    bot.add_cog(n)
