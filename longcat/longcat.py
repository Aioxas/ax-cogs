import discord
import io
from PIL import Image
import random
from redbot.core import commands
from redbot.core.data_manager import bundled_data_path
from redbot.core.bot import Red


class Longcat(commands.Cog):
    """Longcat is long."""

    async def red_delete_data_for_user(self, **kwargs):
        """Nothing to delete."""
        return

    def __init__(self, bot: Red):
        self.bot = bot

    # 42 is the answer to everything
    nreow = ["c" + "a" * i + "t" for i in range(2, 42)]
    mya = ["ny" + "a" * i + "n" for i in range(1, 42)]
    nreow.extend(mya)

    @commands.command(aliases=nreow)
    async def cat(self, ctx):
        """Longcat is long. Use more "a" characters in the command to make a longer cat."""
        # we grab the length of the used prefix and add one letter c
        if str(ctx.message.content.split(ctx.prefix)[1]).startswith("ny"):
            len_prefix = len(ctx.prefix) + 2
        else:
            len_prefix = len(ctx.prefix) + 1
        # now we grab the message itself, take out anything beyond the command itself
        # and substract one to length because of letter t
        len_cat = len(ctx.message.content.split()[0][len_prefix:-1]) - 1
        the_cat = [Image.open(bundled_data_path(self) / "butt.png")]
        trunk = Image.open(bundled_data_path(self) / "trunk.png")
        head = Image.open(bundled_data_path(self) / "head.png")
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
        cat_image_file_object = io.BytesIO()
        cat.save(cat_image_file_object, format="png")
        cat_image_file_object.seek(0)
        cat_image_final = discord.File(fp=cat_image_file_object, filename=f"{random.randint(25000,99999)}_longcat.png")
        await ctx.send(file=cat_image_final)
