from redbot.core import commands
from .emote import Emote


__red_end_user_data_statement__ = (
    "This cog does not store user-specific data."
)


def setup(bot: commands.Bot):
    n = Emote(bot)
    bot.add_listener(n.check_emotes, "on_message")
    bot.add_cog(n)
