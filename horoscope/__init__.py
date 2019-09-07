from .horoscope import Horoscope


def setup(bot):
    bot.add_cog(Horoscope(bot))
