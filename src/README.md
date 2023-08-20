# makemahjongg

v0.1.0  
©2023 Jonas Santoso

Tileset creator for [GNOME Mahjongg](https://wiki.gnome.org/Apps/Mahjongg)

## Install

```shell
pip install makemahjongg
```

## Usage

Given a directory containing 41 images, *makemahjongg* creates a tileset from them that can be used with
GNOME Mahjongg. The tileset is based on the blank tile from GNOME Mahjongg's *smooth* theme.

Usage: `makemahjongg source_directory output_file`

The output file is a PNG which may be copied to Mahjongg's *themes* directory
(`/usr/share/gnome-mahjongg/themes`, YMMV). After copying, it can be used in Mahjongg by opening preferences and
selecting it in the *Theme* dropdown. 

An image can be any size, *makemahjongg* will scale it to fit a tile. Generally images with an aspect ratio
close to 1:1 work best.

*makemahjongg* allows for embedding parameters into the filename. So far only one parameter is recognized:
`resample`. E.g. when a file inside `source_directory` is named this:

&emsp;`31-childlike_empress__resample_NEAREST.png`

...*makemahjongg* will resample the image using the `NEAREST` algorithm instead of the default `LANCZOS`. Valid
values for `resample` are keys into PIL's
[Image.Resampling](https://pillow.readthedocs.io/en/stable/handbook/concepts.html#filters) enum.

Parameters are separated by double underscore. If someone expanded on the [`parseparams`](makemahjongg/tileutil.py#120)
function and added e.g. a *flip* parameter with values of *horizontal*, *vertical*, a filename such as

&emsp;`31-childlike_empress__resample_NEAREST__flip_horizontal.png`

would apply both resampling using `NEAREST` and horizontal flipping.

GNOME Mahjongg's [rules](https://help.gnome.org/users/gnome-mahjongg/stable/bonustiles.html.en) include two
groups of four 'bonus tiles' each, where any tile inside a group matches any other tile within the same group.
In the *postmodern* theme for example, these are the four blue and the four yellow tiles. *makemahjongg* applies
rounded rectangles to these tiles to mark them as bonus tiles, so doing this on the input images is not
required.
