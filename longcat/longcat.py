import os
import time
import discord
from PIL import Image
from redbot.core import commands
from redbot.core.data_manager import bundled_data_path

from redbot.core.bot import Red

BaseCog = getattr(commands, "Cog", object)


class Longcat(BaseCog):
    def __init__(self, bot: Red):
        self.bot = bot
        self.path = bundled_data_path(self)

    # 42 is the answer to everything
    nreow = ["c" + "a" * i + "t" for i in range(2, 42)]
    mya = ["ny" + "a" * i + "n" for i in range(1, 42)]
    nreow.extend(mya)

    @commands.command(aliases=nreow)
    async def cat(self, ctx):
        # we grab the length of the used prefix and add one letter c
        if str(ctx.message.content.split(ctx.prefix)[1]).startswith("ny"):
            len_prefix = len(ctx.prefix) + 2
        else:
            len_prefix = len(ctx.prefix) + 1
        # now we grab the message itself, take out anything beyond the command itself
        # and substract one to length because of letter t
        len_cat = len(ctx.message.content.split()[0][len_prefix:-1]) - 1
        the_cat = [Image.open(self.path / "butt.png")]
        trunk = Image.open(self.path / "trunk.png")
        head = Image.open(self.path / "head.png")
        i = 0
        while i < (len_cat):
            the_cat.append(trunk)
            i += 1
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
        cat.save(self.path / litter_box)
        await ctx.send(file=discord.File(fp=str((self.path / litter_box))))
        os.remove(self.path / litter_box)
