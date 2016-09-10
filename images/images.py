import discord
from discord.ext import commands
from .utils.dataIO import dataIO
from .utils import checks
import os
import re
import aiohttp

# if this seem hard to read/understand, remove the comments. Might make it easier

class Images:
    """Images was made using irdumb's sadface cog's code.
    It works like the emotes cog in another repo.
    The difference is that it's a bit more manual.
    Owner is responsible for it's handling."""

    def __init__(self,bot):
        self.bot = bot
        self.servers = dataIO.load_json('data/images/servers.json')
        self.image = self.servers['image']
        self.images = self.servers['images']
        self.typefail = "Please specify a valid type. PNG or GIF are the only types supported"
    # doesn't make sense to use this command in a pm, because pms aren't in servers
    # mod_or_permissions needs something in it otherwise it's mod or True which is always True

    @commands.command(pass_context=True, no_pm=True)
    @checks.mod_or_permissions(manage_roles=True)
    async def imageset(self, ctx):
        """Enables/Disables images for this server"""
        #default off.
        server = ctx.message.server
        if server.id not in self.servers:
            self.servers[server.id] = False
        else:
            self.servers[server.id] = not self.servers[server.id]
        #for a toggle, settings should save here in case bot fails to send message
        dataIO.save_json('data/images/servers.json', self.servers)
        if self.servers[server.id]:
            await self.bot.say('Images on. Please turn this off in the Red - DiscordBot server. This is only an example cog.')
        else:
            await self.bot.say('Images off.')

    @commands.command(pass_context=True, no_pm=True)
    @checks.mod_or_permissions(manage_roles=True)
    async def add_image(self, ctx, type, name, url):
        """Allows you to add images to the specified type's list
        GIF and PNG are only supported.
        GIFV are special since they can be downloaded as GIF. You can set them as GIF and they will still work.
        [p]add_image gif pan http://i.imgur.com/FFRjKBW.gifv"""
        type = type.lower()
        name = name.lower()
        option = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36', 'CONTENT-TYPE': 'image/{}'.format(type)}
        if not url.endswith((".gif", ".gifv", ".png")):
            await self.bot.say("Links ending in .gif, .png, and .gifv are the only ones accepted, please try again with a valid image link, thanks.")
            return
        if url.endswith(".gifv"):
            url = url.replace(".gifv", ".gif")
        for img in self.images:
            if name in self.images[img]:
                await self.bot.say("This keyword already exists, please use another keyword.")
                return
        if type not in self.image:
            await self.bot.say(self.typefail)
        else:
            try:
                await self.bot.say("Downloading {}.".format(name))
                async with aiohttp.get(url, headers = option) as r:
                    image = await r.read()
                    with open('data/images/images/{}.{}'.format(name, type),'wb') as f:
                        f.write(image)
                    await self.bot.say("Adding {} to the {} list.".format(name, type))
                    self.images[type].append(name)
                    self.images[type].sort()
                dataIO.save_json("data/images/servers.json", self.servers)
                await self.bot.say("{} has been added to the {} list".format(name, type))
            except Exception as e:
                print(e)
                await self.bot.say("It seems your url is not valid,"
                " please make sure you are not typing names with spaces as they are and then the url."
                " If so, do [p]add_image type name_with_spaces url")

    @commands.command(pass_context=True, no_pm=True)
    @checks.mod_or_permissions(manage_roles=True)
    async def del_image(self, ctx, type, name):
        """Allows you to remove images from the specified type's list
        GIF and PNG are only supported."""
        type = type.lower()
        name = name.lower()
        if type not in self.image:
            await self.bot.say(self.typefail)
        else:
            try:
                if type in self.images:
                    if name in self.images[type]:
                        self.images[type].remove(name)
                    else:
                        await self.bot.say("{} is not a valid name, please make sure the name of the"
                        " image that you want to remove is in the type you specified."
                        " Use [p]list_images {} to verify it's there.".format(name, type))
                    dataIO.save_json("data/images/servers.json", self.servers)
                    await self.bot.say("{} has been removed from the {} list".format(name, type))
                    os.remove("data/images/images/{}.{}".format(name,type))
            except FileNotFoundError:
                await self.bot.say("For some unknown reason, your image is not available in the default directory, that is, data/images/images."
                " This means that it can't be removed. But it has been successfully removed from the images list.")

    @commands.command(pass_context=True, no_pm=True)
    @checks.mod_or_permissions(manage_roles=True)
    async def edit_image(self, ctx, type, name, newname):
        """Allows you to edit the keyword that triggers the image from the specified type's list
        GIF and PNG are only supported."""
        type = type.lower()
        name = name.lower()
        if type not in self.image:
            await self.bot.say(self.typefail)
            return
        for img in self.images:
            if newname in self.images[img]:
                await self.bot.say("This keyword already exists, please use another keyword.")
                return
        try:
            if type in self.images:
                if name in self.images[type]:
                    self.images[type].remove(name)
                    self.images[type].append(newname)
                    self.images[type].sort()
                else:
                    await self.bot.say("{} is not a valid name, please make sure the name of the"
                    " image that you want to edit is in the type you specified."
                    " Use [p]list_images {} to verify it's there.".format(name, type))
                dataIO.save_json("data/images/servers.json", self.servers)
                await self.bot.say("{} in the {} list has been renamed to {}".format(name, type, newname))
                os.rename("data/images/images/{}.{}".format(name,type),"data/images/images/{}.{}".format(newname,type))
        except FileNotFoundError:
            await self.bot.say("For some unknown reason, your image is not available in the default directory, that is, data/images/images."
            " This means that it can't be edited. But it has been successfully edited in the image type's list.")

    @commands.command(pass_context=True, no_pm=True)
    @checks.mod_or_permissions(manage_roles=True)
    async def list_images(self, ctx, type):
        """Shows you the specified type's list.
        GIF and PNG are only supported"""
        type = type.lower()
        if type not in self.image:
            await self.bot.say(self.typefail)
        else:
            if not self.images[type]:
                await self.bot.say("Your {} list is empty.".format(type.upper()) +
                " Please add a few images using the [p]add_image function.")
            else:
                s = "\n"
                y = s.join(self.images[type])
                await self.bot.say("List of available images:\n{}".format(y))

    async def check_image(self, message):
        # check if setting is on in this server
        #let images happen in PMs always
        server = message.server
        if message.author.bot:
            return
        for m in self.bot.command_prefix:
            if message.content.startswith(m):
                return
        if server != None:
            if server.id not in self.servers:
                #default off
                self.servers[server.id] = False
                dataIO.save_json("data/images/servers.json", self.servers)
            # images is off, so ignore
            if not self.servers[server.id]:
                return
        msg = message.content.lower().split()
        for m in msg:
            for type in self.images:
                image_find = re.findall("\\b"+"\\b|\\b".join(self.images[type])+"\\b", m)
                if len(image_find) > 0:
                    if image_find[0] in self.images[type]:
                        await self.bot.send_file(message.channel, self.image[type].format(image_find[0]))

def check_folders():
    # create data/images if not there
    if not os.path.exists('data/images/images'):
        print('Creating data/images/images folder...')
        os.mkdir('data/images')
        os.mkdir('data/images/images')

def check_files():
    # create server.json if not there
    # put in default values
    default = {}
    default['images'] = {'png' : [], 'gif' : []}
    default['image'] = {'png' : 'data/images/images/{}.png','gif' : 'data/images/images/{}.gif'}
    if not os.path.isfile('data/images/servers.json'):
        print('Creating default images servers.json...')
        dataIO.save_json('data/images/servers.json', default)

def setup(bot):
    check_folders()
    check_files()
    n = Images(bot)
    # add an on_message listener
    bot.add_listener(n.check_image, 'on_message')
    bot.add_cog(n)
