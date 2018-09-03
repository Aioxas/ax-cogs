from redbot.core import commands
from .emote import Emote


def setup(bot: commands.Bot):
    n = Emote(bot)
    bot.add_listener(n.check_emotes, "on_message")
    bot.add_cog(n)
