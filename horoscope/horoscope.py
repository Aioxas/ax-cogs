from discord.ext import commands
from .utils.chat_formatting import box
import aiohttp
import html
import os
import re

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL = True
except:
    PIL = False


class Horoscope:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="horo", pass_context=True, no_pm=True)
    @commands.cooldown(10, 60, commands.BucketType.user)
    async def _horoscope(self, ctx, *, sign: str):
        """Retrieves today's horoscope for a zodiac sign.
        Works with both signs and birthdays. Make sure to do Month/Day.

        Western Zodiac:
        Capricorn, Aquarius, Pisces, Aries, Taurus, Gemini, Cancer, Leo,
        Virgo, Libra, Scorpio Sagittarius.

        For Chinese zodiac, it's chinese signs or year.

        Chinese Zodiac:
        Ox, Goat, Rat, Snake, Dragon, Tiger, Rabbit, Horse, Monkey,
        Rooster, Dog, Pig

        Examples: [p]horo love, virgo
                  [p]horo chinese, rooster
                  [p]horo daily, virgo
                  [p]horo whatever, virgo
                  [p]horo chinese, 1901
                  [p]horo love, 02/10"""
        option = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0)'
                  ' Gecko/20100101 Firefox/40.1'}
        signs = ["capricorn", "aquarius", "pisces", "aries", "taurus",
                 "gemini", "cancer", "leo", "virgo", "libra", "scorpio",
                 "sagittarius"]
        chinese_signs = ["ox", "goat", "rat", "snake", "dragon", "tiger",
                         "rabbit", "horse", "monkey", "rooster", "dog", "pig"]
        horo_styles = {"love": "http://www.tarot.com/daily-love-horoscope/",
                       "daily": "http://www.tarot.com/daily-horoscope/",
                       "chinese": "http://www.horoscope.com/us/horoscopes/"
                       "chinese/horoscope-chinese-daily-today.aspx?sign="}
        regex = [
         "<div class=\"horoscope-content\">\n<p><b class=\"date\">([^`]*?)<\/p>\n<\/div>",
         "<p class=\"js-today_interp_copy\">([^`]*?)<\/p>"]
        subs = "\n\s*"
        try:
            horos = sign.split(', ')
            style = horos[0]
            horos.remove(style)
            sign = horos[0].lower()
            if style == "chinese":
                if sign not in chinese_signs:
                    sign = self.getchinese_signs(int(sign)).lower()
                uri = horo_styles[style]
                sign_num = str(chinese_signs.index(sign) + 1)
                uir = uri + sign_num
                async with aiohttp.request("GET", uir, headers=option) as resp:
                    test = str(await resp.text())
                    msg = re.findall(regex[0], test)
                    msg = re.sub(subs, "", msg[0]).replace("</b>", "")
                    await self.bot.say("Today's chinese horoscope for the one"
                                       " born in the year of the {} is:\n\n"
                                       .format(sign) + box(msg))
            else:
                if style not in horo_styles:
                    style = "daily"
                if sign not in signs:
                    sign = sign.split("/")
                    Month = sign[0]
                    Day = sign[1]
                    sign = signs[self.getzodiac_signs(Month, Day)]
                uri = horo_styles[style]
                uir = uri + sign
                async with aiohttp.request("GET", uir, headers=option) as resp:
                    test = str(await resp.text())
                    msg = re.findall(regex[1], test)
                    msg = re.sub(subs, "", msg[0])
                    if style == "love":
                        await self.bot.say("Today's love horoscope for "
                                           "**{}** is:\n\n"
                                           .format(sign) + box(msg))
                    else:
                        await self.bot.say("Today's horoscope for "
                                           "**{}** is:\n\n"
                                           .format(sign) + box(msg))

        except IndexError:
            await self.bot.say("Your search is not valid, please follow the "
                               "examples.\n[p]horo love, virgo\n[p]horo life,"
                               " pisces\n[p]horo whatever, sagittarius"
                               "\n[p]horo daily, virgo\n[p]horo chinese,"
                               " rooster")

    def getzodiac_signs(self, Month, Day):
        Month = int(Month)
        Day = int(Day)
        times = [((Month == 12 and Day >= 22)or(Month == 1 and Day <= 19)),
                 ((Month == 1 and Day >= 20)or(Month == 2 and Day <= 17)),
                 ((Month == 2 and Day >= 18)or(Month == 3 and Day <= 19)),
                 ((Month == 3 and Day >= 20)or(Month == 4 and Day <= 19)),
                 ((Month == 4 and Day >= 20)or(Month == 5 and Day <= 20)),
                 ((Month == 5 and Day >= 21)or(Month == 6 and Day <= 20)),
                 ((Month == 6 and Day >= 21)or(Month == 7 and Day <= 22)),
                 ((Month == 7 and Day >= 23)or(Month == 8 and Day <= 22)),
                 ((Month == 8 and Day >= 23)or(Month == 9 and Day <= 22)),
                 ((Month == 9 and Day >= 23)or(Month == 10 and Day <= 22)),
                 ((Month == 10 and Day >= 23)or(Month == 11 and Day <= 21)),
                 ((Month == 11 and Day >= 22)or(Month == 12 and Day <= 21))]
        for m in times:
            if m:
                return times.index(m)

    def getchinese_signs(self, year):
        czodiac = [(1900, "Rat"), (1901, "Ox"), (1902, "Tiger"),
                   (1903, "Rabbit"), (1904, "Dragon"), (1905, "Snake"),
                   (1906, "Horse"), (1907, "Sheep"), (1908, "Monkey"),
                   (1909, "Rooster"), (1910, "Dog"), (1911, "Pig")]
        index = (year - czodiac[0][0]) % 12
        return czodiac[index][1]

    @commands.command(name="tsujiura", no_pm=True, alias=["senbei"])
    @commands.cooldown(10, 60, commands.BucketType.user)
    async def _cookie(self):
        """Retrieves a random fortune cookie fortune."""
        regex = ["class=\"cookie-link\">([^`]*?)<\/a>", "<p>([^`]*?)<\/p>",
                 "(?:\\\\['])", "<strong>([^`]*?)<\/strong>",
                 "<\/strong><\/a>([^`]*?)<br>",
                 "3\)<\/strong><\/a>([^`]*?)<\/div>"]
        url = "http://www.fortunecookiemessage.com"
        await self.file_check()
        async with aiohttp.request("GET", url, headers={"encoding": "utf-8"}) as resp:
            test = str(await resp.text())
            fortune = re.findall(regex[0], test)
            fortest = re.match("<p>", fortune[0])
            if fortest is not None:
                fortune = re.findall(regex[1], fortune[0])
            title = re.findall(regex[3], test)
            info = re.findall(regex[4], test)
            info[0] = html.unescape(info[0])
            dailynum = re.findall(regex[5], test)
            self.fortune_process(fortune[0])
            await self.bot.say("Your fortune is:")
            await self.bot.upload("data/horoscope/cookie-edit.png")
            await self.bot.say("\n" + title[1] +
                               info[1] + "\n" + title[2] + dailynum[0])
            os.remove("data/horoscope/cookie-edit.png")

    async def file_check(self):
        urls = ["https://images-2.discordapp.net/.eJwNwcENwyAMAMBdGABDCWCyDSKIoCYxwuZVdff27qPWvNSuTpHBO8DRudA8NAvN3Kp"
                "uRO2qeXTWhW7IIrmcd32EwQbjMCRMaJNxPmwILxcRg_9Da_yWYoQ3dV5z6fE09f0BC6EjAw.B0sII_QLbL9kJo6Zbb4GuO4MQNw",
                "https://cdn.discordapp.com/attachments/218222973557932032/240223136447070208/FortuneCookieNF.ttf"]
        option = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0)'
                  ' Gecko/20100101 Firefox/40.1'}
        if os.path.exists("data/horoscope/cookie.png"):
            async with aiohttp.request("GET", urls[0], headers=option) as resp:
                test = await resp.read()
                meow = False
                with open("data/horoscope/cookie.png", "rb") as e:
                    if len(test) != len(e.read()):
                        meow = True
                if meow:
                    with open("data/horoscope/cookie.png", "wb") as f:
                        f.write(test)
        elif not os.path.exists("data/horoscope/cookie.png"):
            async with aiohttp.request("GET", urls[0], headers=option) as resp:
                test = await resp.read()
                with open("data/horoscope/cookie.png", "wb") as f:
                    f.write(test)
        if not os.path.exists("data/horoscope/FortuneCookieNF.ttf"):
            async with aiohttp.request("GET", urls[1], headers=option) as resp:
                test = await resp.read()
                with open("data/horoscope/FortuneCookieNF.ttf", "wb") as f:
                    f.write(test)

    @commands.command(name="font", no_pm=True)
    @commands.cooldown(10, 60, commands.BucketType.user)
    async def _font(self, url: str=None):
        """Allows you to set the font that the fortune cookies are shown in.
           Only accepts ttf."""
        option = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0)'
                  ' Gecko/20100101 Firefox/40.1'}

        if url is None :
            url = "https://cdn.discordapp.com/attachments/218222973557932032/240223136447070208/FortuneCookieNF.ttf"
            if os.is_file("data/horoscope/FortuneCookieNF.ttf"):
                return
            else:
                async with aiohttp.request("GET", url, headers=option) as resp:
                    test = await resp.read()
                    with open("data/horoscope/FortuneCookieNF.ttf", "wb") as f:
                        f.write(test)
        elif not url.endswith("ttf"):
            await self.bot.say("This is not a .ttf font, please use a .ttf font. Thanks")
            return
        await self.bot.say("Font has been saved")

    def fortune_process(self, fortune):
        img = Image.open("data/horoscope/cookie.png")
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("data/horoscope/FortuneCookieNF.ttf", 15)
        line = fortune.split()
        sep = " "
        line1 = sep.join(line[:5])
        line2 = sep.join(line[5:10])
        line3 = sep.join(line[10:])
        draw.text((134, 165), line1, (0, 0, 0), font=font, align="center")
        draw.text((134, 180), line2, (0, 0, 0), font=font, align="center")
        draw.text((134, 195), line3, (0, 0, 0), font=font, align="center")
        img.save("data/horoscope/cookie-edit.png")


def check_folders():
    if not os.path.exists("data/horoscope"):
        print("Creating data/horoscope folder...")
        os.mkdir("data/horoscope")


def setup(bot):
    if PIL:
        check_folders()
        n = Horoscope(bot)
        bot.add_cog(n)
    else:
        raise RuntimeError("You need to run 'pip3 install Pillow'")
