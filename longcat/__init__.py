from redbot.core import data_manager, commands
from .longcat import Longcat


def setup(bot: commands.Bot):
    cog = Longcat(bot)
    data_manager.load_bundled_data(cog, __file__)
    bot.add_cog(cog)
