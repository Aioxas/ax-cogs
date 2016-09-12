import discord
from discord.ext import commands
from __main__ import send_cmd_help
from cogs.utils.chat_formatting import *
import aiohttp
import re
import os
from PIL import Image, ImageDraw, ImageFont
import html

class Horoscope:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="horo",pass_context=True, no_pm=True)
    @commands.cooldown(10, 60, commands.BucketType.user)
    async def _horoscope(self, ctx, *, sign : str):
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
        option = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'}
        signs = ["capricorn", "aquarius", "pisces", "aries", "taurus", "gemini", "cancer", "leo", "virgo", "libra", "scorpio", "sagittarius"]
        chinese_signs = ["ox", "goat", "rat", "snake", "dragon", "tiger", "rabbit", "horse", "monkey", "rooster", "dog", "pig"]
        horo_types = {"love" : "http://www.tarot.com/daily-love-horoscope/", "daily" : "http://www.tarot.com/daily-horoscope/",
        "chinese" : "http://www.horoscope.com/us/horoscopes/chinese/horoscope-chinese-daily-today.aspx?sign="}
        regex = ["<div class=\"block-horoscope-chinese-text f16 l20\">([^`]*?)<\/div>", "<p class=\"js-today_interp_copy\">([^`]*?)<\/p>"]
        subs = "\n\s*"
        try:
            horos = sign.split(', ')
            type = horos[0]
            horos.remove(type)
            sign = horos[0].lower()
            if type == "chinese":
                if sign not in chinese_signs:
                    sign = self.getchinese_signs(int(sign)).lower()
                uri = horo_types[type]
                sign_num = str(chinese_signs.index(sign) + 1)
                uir = uri + sign_num
                async with aiohttp.get(uir, headers = option) as resp:
                    test = str(await resp.text())
                    msg = re.findall(regex[0], test)
                    msg = re.sub(subs, "", msg[0])
                    await self.bot.say("Today's chinese horoscope for the one born in the year of the " + sign + " is:\n\n" + box(msg))
            else:
                if type not in horo_types:
                    type = "daily"
                if sign not in signs:
                    sign = sign.split("/")
                    Month = sign[0]
                    Day = sign[1]
                    sign = signs[self.getzodiac_signs(Month, Day)]
                uri = horo_types[type]
                uir = uri + sign
                async with aiohttp.get(uir, headers = option) as resp:
                    test = str(await resp.text())
                    msg = re.findall(regex[1], test)
                    msg = re.sub(subs, "", msg[0])
                    if type == "love":
                        await self.bot.say("Today's love horoscope for **{}** is:\n\n".format(sign) + box(msg))
                    else:
                        await self.bot.say("Today's horoscope for **{}** is:\n\n".format(sign) + box(msg))

        except IndexError:
            await self.bot.say("Your search is not valid, please follow the examples.\n[p]horo love, virgo\n[p]horo life, pisces\n[p]horo whatever, sagittarius\n[p]horo daily, virgo\n[p]horo chinese, rooster")

    def getzodiac_signs(self, Month, Day):
        times = [((int(Month)==12 and int(Day) >= 22)or(int(Month)==1 and int(Day)<= 19)), ((int(Month)==1 and int(Day) >= 20)or(int(Month)==2 and int(Day)<= 17)),
        ((int(Month)==2 and int(Day) >= 18)or(int(Month)==3 and int(Day)<= 19)), ((int(Month)==3 and int(Day) >= 20)or(int(Month)==4 and int(Day)<= 19)),
        ((int(Month)==4 and int(Day) >= 20)or(int(Month)==5 and int(Day)<= 20)), ((int(Month)==5 and int(Day) >= 21)or(int(Month)==6 and int(Day)<= 20)),
        ((int(Month)==6 and int(Day) >= 21)or(int(Month)==7 and int(Day)<= 22)), ((int(Month)==7 and int(Day) >= 23)or(int(Month)==8 and int(Day)<= 22)),
        ((int(Month)==8 and int(Day) >= 23)or(int(Month)==9 and int(Day)<= 22)), ((int(Month)==9 and int(Day) >= 23)or(int(Month)==10 and int(Day)<= 22)),
        ((int(Month)==10 and int(Day) >= 23)or(int(Month)==11 and int(Day)<= 21)), ((int(Month)==11 and int(Day) >= 22)or(int(Month)==12 and int(Day)<= 21))]
        for m in times:
            if m:
                return times.index(m)

    def getchinese_signs(self, year):
        czodiac = [(1900, "Rat"), (1901, "Ox"), (1902, "Tiger"), (1903, "Rabbit"),
        (1904, "Dragon"), (1905, "Snake"), (1906, "Horse"), (1907, "Sheep"),
        (1908, "Monkey"), (1909, "Rooster"), (1910, "Dog"), (1911, "Pig")]
        index = (year - czodiac[0][0]) % 12
        return czodiac[index][1]

    @commands.command(name="cookie", no_pm=True)
    @commands.cooldown(10, 60, commands.BucketType.user)
    async def _cookie(self):
        """Retrieves a random fortune cookie fortune."""
        option = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'}
        regex = ["class=\"cookie-link\">([^`]*?)<\/a>", "<p>([^`]*?)<\/p>", "(?:\\\\['])", "<strong>([^`]*?)<\/strong>", "<\/strong><\/a>([^`]*?)<br>", "3\)<\/strong><\/a>([^`]*?)<\/div>"]
        url = "http://www.fortunecookiemessage.com"
        async with aiohttp.get(url, headers = {"encoding" : "utf-8"}) as resp:
            test = str(await resp.text())
            fortune = re.findall(regex[0], test)
            fortest = re.match("<p>", fortune[0])
            if fortest is not None:
                fortune = re.findall(regex[1], fortune[0])
            title = re.findall(regex[3], test)
            info = re.findall(regex[4], test)
            info[0] = html.unescape(info[0])
            dailynum = re.findall(regex[5], test)
            if not os.path.exists("data/horoscope/cookie.png"):
                url = "http://www.fortunes-cookies.com/wp-content/uploads/2014/04/Fortune_Cookie_18.png"
                async with aiohttp.get(url, headers = option) as resp:
                    test = await resp.read()
                    with open("data/horoscope/cookie.png", "wb") as f:
                        f.write(test)
            self.fortune_process(fortune[0])
            await self.bot.say("Your fortune is:")
            await self.bot.upload("data/horoscope/cookie-edit.png")
            await self.bot.say("\n" + title[0] + info[0] + "\n" + title[1] + info[1] + "\n" + title[2] + dailynum[0])
            os.remove("data/horoscope/cookie-edit.png")

    def fortune_process(self, fortune):
        img = Image.open("data/horoscope/cookie.png").rotate(-5,expand=1)
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("arial.ttf", 15)
        line = fortune.split()
        sep = " "
        line1 = sep.join(line[:7])
        line2 = sep.join(line[7:14])
        line3 = sep.join(line[14:])
        draw.text((210,75),line1,(0,0,0), font=font, align="center")
        draw.text((210,90),line2,(0,0,0), font=font, align="center")
        draw.text((210,105),line3,(0,0,0), font=font, align="center")
        img.save("data/horoscope/cookie-edit.png")

def check_folders():
    if not os.path.exists("data/horoscope"):
        print("Creating data/horoscope folder...")
        os.mkdir("data/horoscope")

def setup(bot):
    check_folders()
    n = Horoscope(bot)
    bot.add_cog(n)
