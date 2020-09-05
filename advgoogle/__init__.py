from .advgoogle import AdvancedGoogle
from redbot.core import commands


__red_end_user_data_statement__ = (
    "This cog stores failed search information when making a search."
    "On a search error, the html of the error-causing page will be written into a file."
    "This is safely deleted if a search is successful. It is only for debugging."
    "Any IPs are replaced with 0.0.0.0 before being written into file."
    "Owners can safely delete any debug data by running [p]googledebugpurge."
)


def setup(bot: commands.Bot):
    bot.add_cog(AdvancedGoogle(bot))
