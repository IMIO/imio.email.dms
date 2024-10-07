# -*- coding: utf-8 -*-
# bin/runpy
from imio.email.dms.utils import get_reduced_size
from PIL import Image
from PIL import ImageOps

import logging
import re
import sys


filename = "/home/sge/Documents/imio/docs/CLIENTS/Flémalle, CPAS/img_orig_20230123_133150.jpg"

EXIF_ORIENTATION = 0x0112
img_size_limit = 1024
modified = False
# http://sylvana.net/jpegcrop/exif_orientation.html

logging.basicConfig()
logger = logging.getLogger("sqlcmd")
logger.setLevel(logging.INFO)
new_name = re.sub(r"\.(jpg|jpeg)", r"_transposed.\1", filename, flags=re.I)
if filename == new_name:
    logger.error("New filename is the same '{}'".format(new_name))
    sys.exit(1)

logger.info("Opening '{}'".format(filename))
img = Image.open(filename)
exif = img.getexif()
orient = exif.get(EXIF_ORIENTATION, 0)
logger.info("Orientation {}".format(orient))
new_img = img

if orient and orient != 1:
    new_img = ImageOps.exif_transpose(img)
    modified = True

is_reduced, new_size = get_reduced_size(new_img.size, img_size_limit)
if is_reduced:
    new_img = new_img.resize(new_size, Image.BICUBIC)
    modified = True

if modified:
    logger.info("Image has been transposed")
    # new_img.save(new_name, format=img.format, optimize=True, quality=75, exif=exif)
    new_img.save(new_name, format=img.format, optimize=True, quality=75)
