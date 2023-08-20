"""makemahjongg v0.1.0
Tileset creator for GNOME Mahjongg

Given a directory containing 41 images, makemahjongg creates a tileset from them that can be used with
GNOME Mahjongg. The tileset is based on the blank tile from GNOME Mahjongg's 'smooth' theme.

Usage: makemahjongg source_directory output_file

The output file is a PNG which may be copied to Mahjongg's 'themes' directory
(/usr/share/gnome-mahjongg/themes, YMMV). After copying, it can be used in Mahjongg by opening preferences and
selecting it in the 'Theme' dropdown. 

An image can be any size, makemahjongg will scale it to fit a tile. Generally images with an aspect ratio close
to 1:1 work best.

makemahjongg allows for embedding parameters into the filename. So far only one parameter is recognized:
resample. E.g. when a file inside source_directory is named this:

  31-childlike_empress__resample_NEAREST.png

...makemahjongg will resample the image using the NEAREST algorithm instead of the default LANCZOS. Valid values
for 'resample' are keys into PIL's Image.Resampling enum
(https://pillow.readthedocs.io/en/stable/handbook/concepts.html#filters).

Parameters are separated by double underscore. If someone expanded on the `parseparams` function below and added
e.g. a 'flip' parameter with values of 'horizontal', 'vertical', a filename such as

  31-childlike_empress__resample_NEAREST__flip_horizontal.png

would apply both resampling using NEAREST and horizontal flipping.

GNOME Mahjongg's rules include two groups of four 'bonus tiles' each, where any tile inside a group matches any
other tile within the same group: https://help.gnome.org/users/gnome-mahjongg/stable/bonustiles.html.en.
In the 'postmodern' theme for example, these are the four blue and the four yellow tiles. makemahjongg applies
rounded rectangles to these tiles to mark them as bonus tiles, so doing this on the input images is not
required.
"""
from glob import glob
from os import path
import re

from PIL import Image, ImageDraw, ImageEnhance


script_dir = path.abspath(path.dirname(__file__))


TILE_WIDTH = 96
TILE_CONTENTWIDTH = 80
TILE_HEIGHT = 132
TILE_CONTENTHEIGHT = 116
TILE_CONTENTXOFFSET = 6
TILE_CONTENTYOFFSET = -6
IMGFILE_BLANK = path.join(script_dir, "blank.png")
IMGFILE_BLANK_SELECTED = path.join(script_dir, "blank_selected.png")
IMGFILE_TILESET_BLANK = path.join(script_dir, "tileset_blank.png")
SELECTED_BRIGHTNESS_FACTOR = 1.25

# There are two 'bonus tile' groups of four tiles each, starting at index 33 and 38 respectively.
# A tile in a bonus group matches with any other tile within the same group.
# ImageDraw is used to mark these groups after tile generation.
#
BONUS_GROUP_1_INDEX = 33
BONUS_GROUP_2_INDEX = 38
BONUS_GROUP_COLORS = [
    None,
    ("#d819ea", "#f58bff"),  # (normal, selected) color for bonus group 1
    ("#1dbf4e", "#77e998"),  # (normal, selected) color for bonus group 2
]


"""The regex used in scanning a filename for parameters
"""
re_param = re.compile(r"__(?P<param>.+?)_(?P<value>.+?)(?=__|\.)")




def mktilepair(source, resample=None):
    """Create a normal and a selected tile for the given image.

    :param source: Input image path
    :param resample: A key into PIL's Image.Resampling enum. When none is given, LANCZOS is used.

    :return: A tuple of PIL.Image objects where the first is the normal tile,
        and the second is the selected tile.
    """
    srcimg = Image.open(source)
    if (srcimg.mode != "RGBA"):
        srcimg = srcimg.convert("RGBA")
    w, h = srcimg.size
    is_landscape = w > h
    if is_landscape:
        scale = TILE_CONTENTWIDTH / w
        if int(scale * h) > TILE_CONTENTHEIGHT:
            scale *= TILE_CONTENTHEIGHT / int(scale * h)
    else:
        scale = TILE_CONTENTHEIGHT / h
        if int(scale * w) > TILE_CONTENTWIDTH:
            scale *= TILE_CONTENTWIDTH / int(scale * w)
    w_scaled, h_scaled = int(scale * w), int(scale * h)
    scaledimg = srcimg.resize(
        (w_scaled, h_scaled),
        resample=resample if resample is not None else Image.Resampling.LANCZOS
    )

    tile = Image.open(IMGFILE_BLANK)
    x_dst = TILE_CONTENTXOFFSET + (TILE_WIDTH - w_scaled) // 2
    y_dst = TILE_CONTENTYOFFSET + (TILE_HEIGHT - h_scaled) // 2
    tile.paste(scaledimg, (x_dst, y_dst), mask=scaledimg)

    tile_selected = Image.open(IMGFILE_BLANK_SELECTED)
    enhancer = ImageEnhance.Brightness(scaledimg)
    scaledimg_selected = enhancer.enhance(SELECTED_BRIGHTNESS_FACTOR)
    tile_selected.paste(scaledimg_selected, (x_dst, y_dst), mask=scaledimg_selected)

    return tile, tile_selected


def parseparams(file):
    """Scan the filename for parameters.

    :param file: Input file path.

    :return: A list of (key, value) tuples.
    """
    basename = path.basename(file)
    params = re_param.findall(basename)
    parsed = {}
    messages = []
    for key, value in params:
        match key.lower():
            case "resample":
                if value in Image.Resampling.__members__:
                    parsed["resample"] = Image.Resampling[value]
                else:
                    messages.append(f"Invalid value for parameter 'resample'.")
            case _:
                messages.append(f"Unknown parameter '{key}'.")
    
    if messages:
        print(f"{basename}:")
        for message in messages:
            print(f"  {message}")

    return parsed


def check_bonus_group(i):
    """Check if the tile currently being created belongs to one of the two bonus groups.

    :param i: Zero-based index of image file inside source directory

    :return: 1 or 2 when it's a bonus tile, otherwise None
    """
    if i - BONUS_GROUP_1_INDEX >= 0 and i - BONUS_GROUP_1_INDEX < 4:
        return 1
    if i - BONUS_GROUP_2_INDEX >= 0 and i - BONUS_GROUP_2_INDEX < 4:
        return 2
    return None


def apply_bonus_group_frame(bonus_group, tile, tile_selected):
    """Draw a rounded rectangle on tiles to mark them as bonus tiles.

    :param bonus_group: Which of the two bonus groups, 1 or 2.
    :param tile: The normal tile.
    :param tile_selected: The selected tile.
    """
    xy = (
        (TILE_CONTENTXOFFSET + 8, 6),
        (TILE_WIDTH - 3, TILE_CONTENTHEIGHT - 2)
    )
    radius = 9
    width = 5
    outline, outline_selected = BONUS_GROUP_COLORS[bonus_group]

    draw = ImageDraw.Draw(tile)
    draw.rounded_rectangle(xy, radius=radius, outline=outline, width=width)

    draw = ImageDraw.Draw(tile_selected)
    draw.rounded_rectangle(xy, radius=radius, outline=outline_selected, width=width)


def mktileset(source_dir):
    """Given a source directory containing images, create a tileset image.

    :param source_dir: Directory containing input images.

    :return: Tileset as PIL.Image object
    """
    tileset = Image.open(IMGFILE_TILESET_BLANK)
    for i, file in enumerate(sorted(glob(f"{source_dir}/*"))):
        params = parseparams(file)
        tile, tile_selected = mktilepair(file, resample=params.get("resample"))

        bonus_group = check_bonus_group(i)
        if bonus_group:
            apply_bonus_group_frame(bonus_group, tile, tile_selected)

        tileset.paste(tile, (i * TILE_WIDTH, 0))
        tileset.paste(tile_selected, (i * TILE_WIDTH, TILE_HEIGHT))
    return tileset
