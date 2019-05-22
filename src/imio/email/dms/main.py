# -*- coding: utf-8 -*-

"""
Usage: process_mails [-h] FILE [--requeue_errors]

Arguments:
    FILE         config file

Options:
    -h --help           Show this screen.
    --requeue_errors    Put email in error status back in waiting for processing
"""
from datetime import datetime
from docopt import docopt
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from hashlib import md5
from imio.email.dms.imap import IMAPEmailHandler
from imio.email.parser.parser import Parser
from io import BytesIO
from pathlib import Path
from smtplib import SMTP
import configparser
import json
import logging
import os
import requests
import sys
import tarfile
import zc.lockfile

logger = logging.getLogger("imio.email.dms")
logger.setLevel(logging.INFO)
chandler = logging.StreamHandler()
chandler.setLevel(logging.INFO)
logger.addHandler(chandler)


ERROR_MAIL = u"""
Problematic mail is attached.\n
Client ID : {}
IMAP login : {}\n
Corresponding exception : {}\n\n
Sorry !\n
"""


def notify(config, mail, error):
    client_id = config["webservice"]["client_id"]
    login = config["mailbox"]["login"]
    smtp_infos = config["smtp"]
    sender = smtp_infos["sender"]
    recipient = smtp_infos["recipient"]

    msg = MIMEMultipart()
    msg["Subject"] = "Error handling an email for client {}".format(client_id)
    msg["From"] = sender
    msg["To"] = recipient

    main_text = MIMEText(ERROR_MAIL.format(client_id, login, error), "plain")
    msg.attach(main_text)

    attachment = MIMEBase("message", "rfc822")
    attachment.set_payload(mail.as_string())
    attachment.add_header("Content-Disposition", "inline")
    msg.attach(attachment)

    smtp = SMTP(smtp_infos["host"], smtp_infos["port"])
    smtp.sendmail(sender, recipient, msg.as_string().encode("utf8"))
    smtp.quit()


def get_mailbox_infos(config):
    mailbox_infos = config["mailbox"]
    host = mailbox_infos["host"]
    port = mailbox_infos["port"]
    ssl = mailbox_infos["ssl"] == "true" and True or False
    login = mailbox_infos["login"]
    password = mailbox_infos["pass"]
    return host, port, ssl, login, password


def get_preview_pdf_path(config, mail_id):
    mail_infos = config["mailinfos"]
    output_dir = mail_infos["pdf-output-dir"]
    filename = "{0}.pdf".format(mail_id.decode("UTF-8"))
    return os.path.join(output_dir, filename)


def send_to_ws(config, headers, pdf_path, attachments):
    ws = config["webservice"]
    client_id = "{0}4{1}".format(ws['client_id'][:2], ws['client_id'][-4:])
    counter_dir = Path(ws['counter_dir'])
    counter_dir.mkdir(exist_ok=True)
    external_id_path = counter_dir / client_id
    if external_id_path.exists() and external_id_path.read_text():
        external_id = int(external_id_path.read_text()) + 1
    else:
        external_id = 1

    tar_path = Path('/tmp') / '{}.tar'.format(external_id)
    with tarfile.open(tar_path, "w") as tar:
        # 1) email pdf printout
        pdf_contents = Path(pdf_path).open('rb').read()
        pdf_info = tarfile.TarInfo(name='email.pdf')
        pdf_info.size = len(pdf_contents)
        tar.addfile(tarinfo=pdf_info, fileobj=BytesIO(pdf_contents))

        # 2) metadata.json
        metadata_contents = json.dumps(headers).encode("utf8")
        metadata_info = tarfile.TarInfo(name='metadata.json')
        metadata_info.size = len(metadata_contents)
        tar.addfile(tarinfo=metadata_info, fileobj=BytesIO(metadata_contents))

        # 3) every attachment file
        for attachment in attachments:
            attachment_contents = attachment['content']
            attachment_info = tarfile.TarInfo(name='/attachments/{}'.format(attachment['filename']))
            attachment_info.size = len(attachment_contents)
            tar.addfile(tarinfo=attachment_info, fileobj=BytesIO(attachment_contents))

    tar_content = tar_path.read_bytes()
    now = datetime.now()
    metadata = {
        "external_id": "{0}{1:08d}".format(client_id, external_id),
        "client_id": client_id,
        "scan_date": now.strftime("%Y-%m-%d"),
        "scan_hour": now.strftime("%H:%M:%S"),
        "user": "testuser",
        "pc": "pc-scan01",
        "creator": "scanner",
        "filesize": len(tar_content),
        "filename": tar_path.name,
        "filemd5": md5(tar_content).hexdigest(),
    }

    auth = (ws['login'], ws['pass'])
    metadata_url = 'http://{ws[host]}:{ws[port]}/dms_metadata/{client_id}/{ws[version]}'.format(
        ws=ws,
        client_id=client_id,
    )
    metadata_req = requests.post(metadata_url,
                                 auth=auth,
                                 json=metadata)

    response_id = json.loads(metadata_req.content)['id']
    upload_url = 'http://{ws[host]}:{ws[port]}/file_upload/{ws[version]}/{id}'.format(
        ws=ws,
        client_id=client_id,
        id=response_id,
    )
    files = {'filedata': ('archive.tar', tar_content, 'application/tar', {'Expires': '0'})}
    upload_req = requests.post(upload_url,
                               auth=auth,
                               files=files)

    external_id_path.write_text(str(external_id))


def process_mails():
    arguments = docopt(__doc__)
    config = configparser.ConfigParser()
    config_file = arguments["FILE"]
    config.read(config_file)

    host, port, ssl, login, password = get_mailbox_infos(config)
    lock = zc.lockfile.LockFile("lock_{0}".format(config['webservice']['client_id']))

    handler = IMAPEmailHandler()
    handler.connect(host, port, ssl, login, password)

    if arguments.get("--requeue_errors"):
        amount = handler.reset_errors()
        logger.info("{} emails in error were put back in waiting state".format(amount))
        handler.disconnect()
        lock.close()
        sys.exit()

    imported = errors = 0
    for mail_info in handler.get_waiting_emails():
        mail_id = mail_info.id
        mail = mail_info.mail
        pdf_path = get_preview_pdf_path(config, mail_id)
        try:
            parser = Parser(mail)
            headers = parser.headers
            attachments = parser.attachments
            parser.generate_pdf(pdf_path)
            send_to_ws(config, headers, pdf_path, attachments)
            handler.mark_mail_as_imported(mail_id)
            imported += 1
        except Exception as e:
            logger.error(e, exc_info=True)
            notify(config, mail, e)
            handler.mark_mail_as_error(mail_id)
            errors += 1

    logger.info(
        "{} emails have been imported. {} emails have caused an error.".format(
            imported, errors
        )
    )
    handler.disconnect()
    lock.close()
