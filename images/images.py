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
    async def add_image(self, ctx, itype, name, url):
        """Allows you to add images to the specified type's list
        GIF and PNG are only supported.
        GIFV are special since they can be downloaded as GIF. You can set them as GIF and they will still work.
        [p]add_image gif pan http://i.imgur.com/FFRjKBW.gifv"""
        itype = itype.lower()
        name = name.lower()
        option = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36', 'CONTENT-TYPE': 'image/{}'.format(itype)}
        if itype not in self.image:
            await self.bot.say(self.typefail)
            return
        if not url.endswith((".gif", ".gifv", ".png")):
            await self.bot.say("Links ending in .gif, .png, and .gifv are the only ones accepted, please try again with a valid image link, thanks.")
            return
        for img in self.images:
            if name in self.images[img]:
                await self.bot.say("This keyword already exists, please use another keyword.")
                return
        if url.endswith(".gifv"):
            url = url.replace(".gifv", ".gif")
        try:
            await self.bot.say("Downloading {}.".format(name))
            async with aiohttp.get(url, headers = option) as r:
                image = await r.read()
                with open('data/images/images/{}.{}'.format(name, itype),'wb') as f:
                    f.write(image)
                await self.bot.say("Adding {} to the {} list.".format(name, itype))
                self.images[itype].append(name)
                self.images[itype].sort()
            dataIO.save_json("data/images/servers.json", self.servers)
            await self.bot.say("{} has been added to the {} list".format(name, itype))
        except Exception as e:
            print(e)
            await self.bot.say("It seems your url is not valid,"
            " please make sure you are not typing names with spaces as they are and then the url."
            " If so, do [p]add_image itype name_with_spaces url")

    @commands.command(pass_context=True, no_pm=True)
    @checks.mod_or_permissions(manage_roles=True)
    async def del_image(self, ctx, itype, name):
        """Allows you to remove images from the specified type's list
        GIF and PNG are only supported."""
        itype = itype.lower()
        name = name.lower()
        if itype not in self.image:
            await self.bot.say(self.typefail)
            return
        try:
            if itype in self.images:
                if name in self.images[itype]:
                    self.images[itype].remove(name)
                else:
                    await self.bot.say("{} is not a valid name, please make sure the name of the"
                    " image that you want to remove is in the type you specified."
                    " Use [p]list_images {} to verify it's there.".format(name, itype))
                dataIO.save_json("data/images/servers.json", self.servers)
                await self.bot.say("{} has been removed from the {} list".format(name, itype))
                os.remove("data/images/images/{}.{}".format(name,itype))
        except FileNotFoundError:
            await self.bot.say("For some unknown reason, your image is not available in the default directory, that is, data/images/images."
            " This means that it can't be removed. But it has been successfully removed from the images list.")

    @commands.command(pass_context=True, no_pm=True)
    @checks.mod_or_permissions(manage_roles=True)
    async def edit_image(self, ctx, itype, name, newname):
        """Allows you to edit the keyword that triggers the image from the specified type's list
        GIF and PNG are only supported."""
        itype = itype.lower()
        name = name.lower()
        if itype not in self.image:
            await self.bot.say(self.typefail)
            return
        for img in self.images:
            if newname in self.images[img]:
                await self.bot.say("This keyword already exists, please use another keyword.")
                return
        try:
            if itype in self.images:
                if name in self.images[itype]:
                    self.images[itype].remove(name)
                    self.images[itype].append(newname)
                    self.images[itype].sort()
                else:
                    await self.bot.say("{} is not a valid name, please make sure the name of the"
                    " image that you want to edit is in the type you specified."
                    " Use [p]list_images {} to verify it's there.".format(name, itype))
                    return
                dataIO.save_json("data/images/servers.json", self.servers)
                await self.bot.say("{} in the {} list has been renamed to {}".format(name, itype, newname))
                os.rename("data/images/images/{}.{}".format(name,itype),"data/images/images/{}.{}".format(newname,itype))
        except FileNotFoundError:
            await self.bot.say("For some unknown reason, your image is not available in the default directory, that is, data/images/images."
            " This means that it can't be edited. But it has been successfully edited in the image type's list.")

    @commands.command(pass_context=True, no_pm=True)
    @checks.mod_or_permissions(manage_roles=True)
    async def list_images(self, ctx, itype, style):
        """Shows you the specified type's list.
        GIF and PNG are only supported
        Supported styles: [p]list_images png 10 (shows 10 images per page)
        and [p]list_images png a (shows all the images beginning with a)"""
        itype = itype.lower()
        style = style.lower()
        istyles = self.images[itype]
        if itype not in self.image:
            await self.bot.say(self.typefail)
            return
        if not istyles:
            await self.bot.say("Your {} list is empty.".format(itype.upper()) +
            " Please add a few images using the [p]add_image function.")
            return
        if style.isdigit():
            if style == "0":
                await self.bot.say("Only numbers from 1 to infinite are accepted.")
                return
            style = int(style)
            istyle = istyles
        elif style.isalpha():
            istyle = []
            for i in range(len(istyles)):
                ist = re.findall("\\b"+style+"\\w+", istyles[i])
                istyle = istyle + ist
            style = 10
        else:
            await self.bot.say("Your list style is not correct, please use one"
                                " of the accepted styles, either do [p]list_images png A"
                                " or [p]list_images png 10")
            return
        s = "\n"
        count = style
        counter = len(istyle) + count
        while style <= counter:
            if style <= count:
                y = s.join(istyle[:style])
                await self.bot.say("List of available images:\n{}".format(y))
                if style > len(istyle):
                    return
                style += count
            elif style > count:
                style2 = style - count
                y = s.join(istyle[style2:style])
                await self.bot.say("Continuation:\n{}".format(y))
                if style > len(istyle):
                    return
                style += count
            await self.bot.say("Do you want to continue seeing the list? Yes/No")
            answer = await self.bot.wait_for_message(timeout=15,
                                         author=ctx.message.author)
            if answer is None:
                return
            elif answer.content.lower().strip() == "yes":
                continue
            else:
                return

    @commands.command(pass_context=True, no_pm=True)
    @checks.mod_or_permissions(manage_roles=True)
    async def compare_images(self, ctx, style, itype : str=None):
        """Allows you to compare keywords to files
        or files to keywords and then make sure that
        they all coincide
        Keywords to Files name: K2F
        Files to Keywords name: F2K
        [p]compare_images png K2F"""
        style = style.lower()
        if itype is not None:
            itype = itype.lower()
        styleset = ["k2f", "f2k"]
        if style not in styleset:
            return
        count = 0
        msg = "Keywords deleted due to missing files in {} list:\n".format
        c = list()
        for entry in os.scandir("data/images/images"):
            c.append(entry.name)
        missing = list()
        if style == styleset[0]:
            if itype not in self.images:
                await self.bot.say(self.typefail)
                return
            for n in self.images[itype]:
                cat = "|".join(c)
                if not n.isalnum():
                    z = re.compile(r"\B"+n+r"."+itype+r"\b")
                else:
                    z = re.compile(r"\b"+n+r"."+itype+r"\b")
                if z.search(cat) is None:
                    missing.append(n)
            if not missing:
                await self.bot.say("All files and keywords are accounted for")
                return
            for m in missing:
                if m in self.images[itype]:
                    self.images[itype].remove(m)
            dataIO.save_json("data/images/servers.json", self.servers)
            s = "\n"
            style = 10
            counter = len(missing) + 10
            while style <= counter:
                if style <= 10:
                    y = s.join(missing[:style])
                    await self.bot.say(msg(itype.upper()) + y)
                    if style >= len(missing):
                        return
                    style += 10
                elif style > 10:
                    style2 = style - 10
                    y = s.join(missing[style2:style])
                    await self.bot.say("Continuation:\n{}".format(y))
                    if style >= len(missing):
                        return
                    style += 10
                await self.bot.say("Do you want to continue seeing the list? Yes/No")
                answer = await self.bot.wait_for_message(timeout=15,
                                             author=ctx.message.author)
                if answer is None:
                    return
                elif answer.content.lower().strip() == "yes":
                    continue
                else:
                    return

        elif style == styleset[1]:
            for cat in c:
                listing = cat.split('.')
                if listing[0] not in self.images[listing[1]]:
                    self.images[listing[1]].append(listing[0])
                    self.images[listing[1]].sort()
                    count += 1
            if count == 0:
                await self.bot.say("All files and keywords are accounted for")
                return
            dataIO.save_json("data/images/servers.json", self.servers)
            await self.bot.say(str(count) + " Keywords have been successfully added to the"
                                                                        " type lists")
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
            for itype in self.images:
                for n in self.images[itype]:
                    if not n.isalnum():
                        regex = re.compile(r"\B"+n+r"\b")
                    else:
                        regex = re.compile(r"\b"+n+r"\b")
                    image_find = regex.findall(m)
                    if image_find:
                        await self.bot.send_file(message.channel, self.image[itype].format(image_find[0]))

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
