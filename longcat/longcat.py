import os
import time
from PIL import Image
from discord.ext import commands


class Longcat:
    def __init__(self, bot):
        self.bot = bot
        self.path = "data/longcat/"

    # 42 is the answer to everything
    nreow = ["c"+"a"*i+"t" for i in range(2, 42)]
    mya = ["ny"+"a"*i+"n" for i in range(2, 42)]

    @commands.command(pass_context=True, aliases=nreow)
    async def cat(self, ctx):
        # we grab the length of the used prefix and add one letter c
        len_prefix = len(ctx.prefix) + 1
        # now we grab the message itself, take out anything beyond the command itself
        # and substract one to length because of letter t
        len_cat = len(ctx.message.content.split()[0][len_prefix:-1])
        the_cat = [Image.open(self.path + "butt.png")]
        trunk = Image.open(self.path + "trunk.png")
        head = Image.open(self.path + "head.png")
        for i in range(len_cat-1):
            the_cat.append(trunk)
        the_cat.append(head)
        widths, heights = zip(*(i.size for i in the_cat))
        total_widths = sum(widths)
        total_heights = max(heights)
        cat = Image.new("RGBA", (total_widths, total_heights))
        x_offset = 0
        for im in the_cat:
            cat.paste(im, (x_offset, 0))
            x_offset += im.size[0]
        # I'm giving it a name based on a timestamp, this prevents future problems
        litter_box = str(time.time()).split(".")[0] + ".png"
        cat.save(self.path + litter_box)
        await self.bot.upload(self.path + litter_box)
        os.remove(self.path + litter_box)

    @commands.command(pass_context=True, aliases=mya)
    async def nyan(self, ctx):
        # we grab the length of the used prefix and add two letter ny
        len_prefix = len(ctx.prefix) + 2
        # now we grab the message itself, take out anything beyond the command itself
        # and substract one to length because of letter n
        len_cat = len(ctx.message.content.split()[0][len_prefix:-1])
        the_cat = [Image.open(self.path + "butt.png")]
        trunk = Image.open(self.path + "trunk.png")
        head = Image.open(self.path + "head.png")
        for i in range(len_cat-1):
            the_cat.append(trunk)
        the_cat.append(head)
        widths, heights = zip(*(i.size for i in the_cat))
        total_widths = sum(widths)
        total_heights = max(heights)
        cat = Image.new("RGBA", (total_widths, total_heights))
        x_offset = 0
        for im in the_cat:
            cat.paste(im, (x_offset, 0))
            x_offset += im.size[0]
        # I'm giving it a name based on a timestamp, this prevents future problems
        litter_box = str(time.time()).split(".")[0] + ".png"
        cat.save(self.path + litter_box)
        await self.bot.upload(self.path + litter_box)
        os.remove(self.path + litter_box)

def check_folders():
    f = "data/longcat"
    if not os.path.exists(f):
        print("creating data/longcat directory")
        os.mkdir(f)


def setup(bot):
    check_folders()
    bot.add_cog(Longcat(bot))
