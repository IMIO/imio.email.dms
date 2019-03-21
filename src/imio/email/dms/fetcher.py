# -*- coding: utf-8 -*-

import email
import imaplib
import logging

logger = logging.getLogger("imio.email.dms")


class MailData(object):
    def __init__(self, mail_id, mail_obj):
        self.id = mail_id
        self.mail = mail_obj


class IMAPEmailFetcher(object):
    """Handle IMAP mails"""

    connection = None

    def connect(self, host, port, ssl, login, password):
        """Connect and login to IMAP server"""
        if ssl:
            self.connection = imaplib.IMAP4_SSL(host, port)
        else:
            self.connection = imaplib.IMAP4(host, port)
        self.connection.login(login, password)
        self.connection.select("INBOX")

    def disconnect(self):
        """Disconnect from IMAP server"""
        self.connection.close()
        self.connection.logout()

    def get_unread_emails(self):
        """Fetch all unread messages"""
        res, data = self.connection.search(None, "Answered")
        if res != "OK":
            logger.error("Unable to fetch mails")
            return []
        unreads = []
        for mail_id in data[0].split():
            res, mail_data = self.connection.fetch(mail_id, "(RFC822)")
            if res != "OK":
                logger.error("Unable to fetch mail {0}".format(mail_id))
                continue
            mail_body = mail_data[0][1].decode("utf-8")
            mail = email.message_from_string(mail_body)
            mail_infos = MailData(mail_id, mail)
            unreads.append(mail_infos)
        return unreads

    def mark_mail_as_read(self, mail_id):
        """Mark Seen flag on specified mail"""
        self.connection.imap.store(mail_id, "+FLAGS", "\Seen")

    def mark_mail_as_error(self, mail_id):
        """Mark flag on specified mail"""
        self.connection.store(mail_id, "+FLAGS", "FLAGGED")
