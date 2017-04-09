from PIL import Image
from discord.ext import commands
import os


class Longcat:

    def __init__(self, bot):
        self.bot = bot
        self.path = "data/longcat/"

    nreow = ["c"+"a"*i+"t"for i in range(2, 20)]

    @commands.command(pass_context=True, aliases=nreow)
    async def cat(self, ctx):
        # we grab the length of the used prefix and add one letter c
        len_prefix = len(ctx.prefix) + 1
        # now we grab the message itself, take out anything beyond the command itself
        # and substract one to length because of letter t
        len_cat = len(ctx.message.content.split()[0][len_prefix:-1])
        len_cat = 20 if len_cat > 20 else len_cat  # To prevent abuse we set a max of 20
        cat_butt = [Image.open(self.path + "butt.png")]
        trunk = Image.open(self.path + "trunk.png")
        head = Image.open(self.path + "head.png")
        for i in range(len_cat-1):
            cat_butt.append(trunk)
        cat_butt.append(head)
        widths, heights = zip(*(i.size for i in head))
        total_widths = sum(widths)
        total_heights = max(heights)
        new_im = Image.new("RGBA", (total_widths, total_heights))
        x_offset = 0
        for im in cat_butt:
            new_im.paste(im, (x_offset, 0))
            x_offset += im.size[0]
        cat = "test.png"
        new_im.save(self.path + cat)
        await self.bot.upload(self.path + "test.png")
        os.remove(self.path + "test.png")


def check_folders():
    f = "data/longcat"
    if not os.path.exists(f):
        print("creating data/longcat directory")
        os.mkdir(f)


def setup(bot):
    check_folders()
    bot.add_cog(Longcat(bot))
