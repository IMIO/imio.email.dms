# -*- coding: utf-8 -*-

import email
import imaplib
import logging

logger = logging.getLogger("imio.email.dms")


class MailData(object):
    def __init__(self, mail_id, mail_obj):
        self.id = mail_id
        self.mail = mail_obj


class IMAPEmailHandler(object):
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

    def reset_errors(self):
        """Fetch all messages in error status and put them back in waiting"""
        res, data = self.connection.search(None, "KEYWORD error")
        if res != "OK":
            logger.error("Unable to fetch mails")
            return []
        amount = 0
        for mail_id in data[0].split():
            amount += 1
            self.mark_reset_error(mail_id)
        return amount

    def get_waiting_emails(self):
        """Fetch all waiting messages"""
        res, data = self.connection.search(None, "NOT KEYWORD imported")
        if res != "OK":
            logger.error("Unable to fetch mails")
            return []
        waiting = []
        for mail_id in data[0].split():
            res, mail_data = self.connection.fetch(mail_id, "(RFC822)")
            if res != "OK":
                logger.error("Unable to fetch mail {0}".format(mail_id))
                continue
            if not self.should_handle(mail_id):
                continue
            mail_body = mail_data[0][1].decode("utf-8")
            mail = email.message_from_string(mail_body)
            mail_infos = MailData(mail_id, mail)
            waiting.append(mail_infos)
        return waiting

    def should_handle(self, mail_id):
        res, flags_data = self.connection.fetch(mail_id, '(FLAGS)')
        if res != "OK":
            logger.error("Unable to fetch flags for mail {0}".format(mail_id))
            return False
        flags = imaplib.ParseFlags(flags_data[0])
        if b"imported" in flags or b"error" in flags:
            return False
        return True

    def mark_reset_error(self, mail_id):
        """Reset 'error' / 'waiting' flags on specified mail"""
        self.connection.store(mail_id, "-FLAGS", "imported")
        self.connection.store(mail_id, "-FLAGS", "error")
        self.connection.store(mail_id, "+FLAGS", "waiting")

    def mark_mail_as_imported(self, mail_id):
        """(Un)Mark 'imported' / 'waiting' flags on specified mail"""
        self.connection.store(mail_id, "-FLAGS", "waiting")
        self.connection.store(mail_id, "+FLAGS", "imported")

    def mark_mail_as_error(self, mail_id):
        """(Un)Mark 'error' / 'waiting' flags on specified mail"""
        self.connection.store(mail_id, "-FLAGS", "waiting")
        self.connection.store(mail_id, "+FLAGS", "error")
