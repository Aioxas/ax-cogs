import discord
import aiohttp
from discord.ext import commands
from .utils import checks
from __main__ import send_cmd_help
from random import choice
import os
import logging
import re
from cogs.utils.chat_formatting import *
import urllib

class AdvancedGoogle:

	def __init__(self, bot):
		self.bot = bot
		self.option = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'}
		self.break_regex = re.compile("<br \/>")
		self.CR_LF_removal_regex = re.compile("(?:\\\\[rn])")
		self.single_quote_regex = re.compile("(?:\\\\['])")
		
	@commands.command(name = "advgoogle", pass_context=True, no_pm=True)
	async def _advgoogle(self, ctx, text):
		"""Its google, you search with it.
		Example: google A french pug

		Special search options are avaiable; Image, Maps
		Example: google image You know, for kids!
		Another example: google maps New York
		LEGACY EDITION! SEE HERE! https://twentysix26.github.io/Red-Docs/red_cog_approved_repos/#refactored-cogs
		
		Originally made by Kowlin https://github.com/Kowlin/refactored-cogs edited by Axioxas"""
		search_type = ctx.message.content[len(ctx.prefix+ctx.command.name)+1:].lower().split(" ")
		
		#Start of Image
		if search_type[0] == "image":
			search_valid = str(ctx.message.content[len(ctx.prefix+ctx.command.name)+1:].lower())
			if search_valid == "image":
				await self.bot.say("Please actually search something")
			else:
				uri = "https://www.google.com/search?tbm=isch&tbs=isz:m&q="
				quary = str(ctx.message.content[len(ctx.prefix+ctx.command.name)+7:].lower())
				encode = urllib.parse.quote_plus(quary,encoding='utf-8',errors='replace')
				uir = uri+encode
				async with aiohttp.get(uir, headers = self.option) as resp:
					test = await resp.content.read()
					imageregex = re.compile(",\"ou\":\"([^`]*?)\"")
					unicoded = test.decode("unicode_escape")
					query_find = imageregex.findall(unicoded)
					try:
						url = choice(query_find)
						await self.bot.say(url)
					except IndexError:
						await self.bot.say("Your search yielded no results.")
			#End of Image
		#Start of Maps
		elif search_type[0] == "maps":
			search_valid = str(ctx.message.content[len(ctx.prefix+ctx.command.name)+1:].lower())
			if search_valid == "maps":
				await self.bot.say("Please actually search something")
			else:
				uri = "https://www.google.com/maps/search/"
				quary = str(ctx.message.content[len(ctx.prefix+ctx.command.name)+6:].lower())
				encode = urllib.parse.quote_plus(quary,encoding='utf-8',errors='replace')
				uir = uri+encode
				await self.bot.say(uir, header = self.option)
			#End of Maps
		#Start of generic search
		else:
			uri = "https://www.google.com/search?q="
			quary = str(ctx.message.content[len(ctx.prefix+ctx.command.name)+1:])
			encode = urllib.parse.quote_plus(quary,encoding='utf-8',errors='replace')
			uir = uri+encode
			async with aiohttp.get(uir, headers = self.option) as resp:
				test = await resp.content.read()
				searchregex = re.compile("<h3 class=\"r\"><a href=\"\/url\?url=([^`]*?)&amp;")
				searchregex2 = re.compile("<h3 class=\"r\"><a href=\"([^`]*?)\"")
				searchregex3 = re.compile("<h3 class=\"r\"><a href=\"http:\/\/www.google.com\/url\?url=([^`]*?)&amp;")
				query_find = searchregex.findall("{}".format(test))
				if query_find == []:
					query_find = searchregex2.findall("{}".format(test))
					try:
						if re.search("\/url?url=", query_find[0]) == True:
							query_find = query_find[0]
							m = re.search("\/url?url=", query_find)
							query_find = query_find[:m.start()] + query_find[m.end():]
							decode = self.unescape(query_find)
							await self.bot.say("Here is your link: {}".format(decode))
						else:
							decode = self.unescape(query_find[0])
							await self.bot.say("Here is your link: {}".format(decode))
					except IndexError:
						await self.bot.say("Your search yielded no results.")
				elif re.search("\/url?url=", query_find[0]) == True:
					query_find = query_find[0]
					m = re.search("\/url?url=", query_find)
					query_find = query_find[:m.start()] + query_find[m.end():]
					decode = self.unescape(query_find)
					await self.bot.say("Here is your link: {}".format(decode))
				else:
					query_find = query_find[0]
					decode = self.unescape(query_find)
					await self.bot.say("Here is your link: {} ".format(decode))
			#End of generic search
					
	def unescape(self, query):
		break_sub = self.break_regex.sub("\n", query)
		CR_LF_sub = self.CR_LF_removal_regex.sub("", break_sub)
		single_quote_sub = self.single_quote_regex.sub("'", CR_LF_sub)
		percent_sub = re.sub("%25", "%", single_quote_sub)
		left_parentheses_sub = re.sub("\(", "%28", percent_sub)
		right_parentheses_sub = re.sub("\)", "%29", left_parentheses_sub)
		return right_parentheses_sub
		
def setup(bot):
	n = AdvancedGoogle(bot)
	bot.add_cog(n)
