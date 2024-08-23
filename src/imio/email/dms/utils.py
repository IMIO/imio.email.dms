# -*- coding: utf-8 -*-
from datetime import datetime
from email import generator
from email import utils
from imio.email.dms import dev_mode

import os
import six


try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path  # noqa


def safe_unicode(value, encoding="utf-8"):
    """Converts a value to unicode, even it is already a unicode string."""
    if isinstance(value, unicode):  # noqa
        return value
    elif isinstance(value, basestring):  # noqa
        try:
            value = unicode(value, encoding)  # noqa
        except:
            value = value.decode("utf-8", "replace")
    return value


def save_as_eml(path, message):
    with open(path, "w") as emlfile:
        gen = generator.Generator(emlfile)
        gen.flatten(message)


def reception_date(message):
    """Returns localized mail date"""
    date_str = message.get("date")
    r_date = u""
    if date_str:
        date_tuple = utils.parsedate_tz(date_str)
        if date_tuple:
            date = datetime.fromtimestamp(utils.mktime_tz(date_tuple))
            r_date = date.strftime("%Y-%m-%d %H:%M")
    return r_date


def get_next_id(config, dev_infos):
    """Get next id from counter file"""
    ws = config["webservice"]
    client_id = "{0}Z{1}".format(ws["client_id"][:2], ws["client_id"][-4:])
    counter_dir = Path(ws["counter_dir"])
    next_id_path = counter_dir / client_id
    if next_id_path.exists() and next_id_path.read_text():
        next_id = int(next_id_path.read_text()) + 1
    else:
        next_id = 1
    if dev_mode:
        if dev_infos["nid"] is None:
            dev_infos["nid"] = next_id
        else:
            dev_infos["nid"] += 1
            return dev_infos["nid"], client_id
    return next_id, client_id


def get_reduced_size(size, img_size_limit):
    """Returns a bool if size has been reduced and the new size tuple"""
    greatest = 0
    if size[0] < size[1]:
        greatest = 1
    if size[greatest] < img_size_limit:
        return False, None
    lowest = int(not bool(greatest))
    percent = img_size_limit / float(size[greatest])
    new_size = [0, 0]
    new_size[greatest] = img_size_limit
    new_size[lowest] = int((float(size[lowest]) * float(percent)))
    return True, tuple(new_size)


def get_unique_name(filename, files):
    """Get a filename and eventually rename it so it is unique in files list"""
    new_filename = filename
    counter = 1
    filename, extension = os.path.splitext(filename)
    while new_filename in files:
        new_filename = "{} ({}){}".format(filename, counter, extension)
        counter += 1
    files.append(new_filename)
    return new_filename


def set_next_id(config, current_id):
    """Set current id in counter file"""
    ws = config["webservice"]
    client_id = "{0}Z{1}".format(ws["client_id"][:2], ws["client_id"][-4:])
    counter_dir = Path(ws["counter_dir"])
    next_id_path = counter_dir / client_id
    current_id_txt = str(current_id) if six.PY3 else str(current_id).decode()
    next_id_path.write_text(current_id_txt)
