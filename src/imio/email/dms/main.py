# -*- coding: utf-8 -*-

"""
Usage: process_mails [-h] FILE

Arguments:
    FILE         config file

Options:
    -h --help
"""


from docopt import docopt
from imio.email.dms.fetcher import IMAPEmailFetcher
from imio.email.parser.parser import Parser
import configparser
import os
import zc.lockfile


def get_mailbox_infos(config_filename):
    config = configparser.ConfigParser()
    config.read(config_filename)
    mailbox_infos = config["mailbox"]
    host = mailbox_infos["host"]
    port = mailbox_infos["port"]
    ssl = mailbox_infos["ssl"] == "true" and True or False
    login = mailbox_infos["login"]
    password = mailbox_infos["pass"]
    return host, port, ssl, login, password


def get_preview_pdf_path(config_filename, mail_id):
    config = configparser.ConfigParser()
    config.read(config_filename)
    mailbox_infos = config["mailinfos"]
    output_dir = mailbox_infos["pdf-output-dir"]
    filename = "{0}.pdf".format(mail_id.decode('UTF-8'))
    return os.path.join(output_dir, filename)


def process_mails():
    arguments = docopt(__doc__)
    config_file = arguments["FILE"]
    host, port, ssl, login, password = get_mailbox_infos(config_file)
    lock = zc.lockfile.LockFile("lock")
    fetcher = IMAPEmailFetcher()
    fetcher.connect(host, port, ssl, login, password)
    for mail_info in fetcher.get_unread_emails():
        mail_id = mail_info.id
        mail = mail_info.mail
        pdf_path = get_preview_pdf_path(config_file, mail_id)
        try:
            parser = Parser(mail)
            headers = parser.headers
            print(headers)
            attachments = parser.attachments
            print([a.filename for a in attachments])
            parser.generate_pdf(pdf_path)
            # send_to_ws ...
            fetcher.mark_mail_as_read(mail_id)
        except:
            fetcher.mark_mail_as_error(mail_id)
    fetcher.disconnect()
    lock.close()
