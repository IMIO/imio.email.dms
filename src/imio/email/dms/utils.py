# -*- coding: utf-8 -*-
from datetime import datetime
from email import generator
from email import utils
from io import BytesIO
from PIL import Image


def safe_unicode(value, encoding='utf-8'):
    """Converts a value to unicode, even it is already a unicode string.
    """
    if isinstance(value, unicode):
        return value
    elif isinstance(value, basestring):
        try:
            value = unicode(value, encoding)
        except:
            value = value.decode('utf-8', 'replace')
    return value


def save_as_eml(path, message):
    with open(path, 'w') as emlfile:
        gen = generator.Generator(emlfile)
        gen.flatten(message)


def reception_date(message):
    """Returns localized mail date"""
    date_str = message.get('date')
    r_date = u''
    if date_str:
        date_tuple = utils.parsedate_tz(date_str)
        if date_tuple:
            date = datetime.fromtimestamp(utils.mktime_tz(date_tuple))
            r_date = date.strftime('%Y-%m-%d %H:%M')
    return r_date


def modify_attachments(attachments):
    """Reduce size attachments"""
    new_lst = []
    for dic in attachments:
        # we pass inline image, often used in signatures. This image will be in generated pdf
        if dic['type'].startswith('image/') and dic['disp'] == 'inline':
            continue
#        if dic['type'].startswith('image/') and dic['size'] > 1000000:
#         if dic['type'].startswith('image/'):
#             img = Image.open(BytesIO(dic['content']))
#             filename = dic['filename']
        new_lst.append(dic)
    return new_lst
