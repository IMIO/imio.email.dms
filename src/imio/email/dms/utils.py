# -*- coding: utf-8 -*-
from datetime import datetime
from email import generator
from email import utils


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
    date_str = message.get('date')
    r_date = u''
    if date_str:
        date_tuple = utils.parsedate_tz(date_str)
        if date_tuple:
            date = datetime.fromtimestamp(utils.mktime_tz(date_tuple))
            r_date = date.strftime('%Y-%m-%d %H:%M')
    return r_date
