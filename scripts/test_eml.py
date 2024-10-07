# -*- coding: utf-8 -*-
# bin/runpy
from email.policy import default
from imio.email.parser.parser import Parser  # noqa

import argparse
import email


parser = argparse.ArgumentParser(description="Test email analysis.")
parser.add_argument("eml_file", help="email file")
ns = parser.parse_args()


with open(ns.eml_file) as fp:
    mail = email.message_from_file(fp, policy=default)
    mail.__setitem__("X-Forwarded-For", "0.0.0.0")  # to be considered as main mail
    str0 = mail.as_string()
    parser = Parser(mail, False, "")
    str1 = parser.message.as_string()
    # mail.attach(MIMEText("<html><body><p></p></body></html>", "html"))
    parser.add_body(mail, "<html><body><p></p></body></html>")
    mail.get_body(preferencelist=("html", "plain"))
    strn = parser.message.as_string()
    [at for at in mail.iter_attachments()]
