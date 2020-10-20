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
from imio.email.parser.parser import Parser  # noqa
from io import BytesIO
from smtplib import SMTP
import configparser
import json
import logging
import os
import requests
import six
import sys
import tarfile
import zc.lockfile

try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path

logger = logging.getLogger("imio.email.dms")
logger.setLevel(logging.INFO)
chandler = logging.StreamHandler()
chandler.setLevel(logging.INFO)
logger.addHandler(chandler)


ERROR_MAIL = u"""
Problematic mail is attached.\n
Client ID : {0}
IMAP login : {1}\n
Corresponding exception : {2.__class__}
{2.message}\n
"""

UNSUPPORTED_ORIGIN_EMAIL = u"""
Dear user,

The attached email has been refused because it wasn't sent to us as an attachment.\n
\n
Please try again, by following one of these methods.\n
\n
If you are using Microsoft Outlook:\n
- In the ribbon, click on the More dropdown button next to the standard Forward button\n
- Choose Forward as Attachment\n
- Send the opened draft to the GED import address.\n
\n
If you are using Mozilla Thunderbird:\n
- Open the email you want to import into the GED.\n
- Click on the menu Message > Forward As > Attachment.\n
- Send the opened draft to the GED import address.\n
\n
Please excuse us for the inconvenience.\n
"""


class DmsMetadataError(Exception):
    """ The response from the webservice dms_metadata route is not successful """


class FileUploadError(Exception):
    """ The response from the webservice file_upload route is not successful """


def notify_exception(config, mail, error):
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

    smtp = SMTP(str(smtp_infos["host"]), int(smtp_infos["port"]))
    msg_content = msg.as_string().encode("utf8") if six.PY3 else msg.as_string()
    smtp.sendmail(sender, recipient, msg_content)
    smtp.quit()


def notify_unsupported_origin(config, mail, from_):
    smtp_infos = config["smtp"]
    sender = smtp_infos["sender"]

    msg = MIMEMultipart()
    msg["Subject"] = "Error importing email into iA.docs"
    msg["From"] = sender
    msg["To"] = from_

    main_text = MIMEText(UNSUPPORTED_ORIGIN_EMAIL, "plain")
    msg.attach(main_text)

    attachment = MIMEBase("message", "rfc822")
    attachment.set_payload(mail.as_string())
    attachment.add_header("Content-Disposition", "inline")
    msg.attach(attachment)

    smtp = SMTP(str(smtp_infos["host"]), int(smtp_infos["port"]))
    msg_content = msg.as_string().encode("utf8") if six.PY3 else msg.as_string()
    smtp.sendmail(sender, from_, msg_content)
    smtp.quit()


def get_mailbox_infos(config):
    mailbox_infos = config["mailbox"]
    host = str(mailbox_infos["host"])
    port = int(mailbox_infos["port"])
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
    next_id_path = counter_dir / client_id
    if next_id_path.exists() and next_id_path.read_text():
        next_id = int(next_id_path.read_text()) + 1
    else:
        next_id = 1

    external_id = "{0}{1:08d}".format(client_id, next_id)
    tar_path = Path('/tmp') / '{}.tar'.format(external_id)
    with tarfile.open(str(tar_path), "w") as tar:
        # 1) email pdf printout
        pdf_contents = Path(pdf_path).open('rb').read()
        pdf_info = tarfile.TarInfo(name='email.pdf')
        pdf_info.size = len(pdf_contents)
        tar.addfile(tarinfo=pdf_info, fileobj=BytesIO(pdf_contents))

        # 2) metadata.json
        metadata_contents = json.dumps(headers).encode("utf8") if six.PY3 else json.dumps(headers)
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
        "external_id": external_id,
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
    metadata_req = requests.post(metadata_url, auth=auth, json=metadata)
    req_content = json.loads(metadata_req.content)
    if not req_content['success'] or 'id' not in req_content:
        msg = u"code: '{}', error: '{}', metadata: '{}'".format(req_content['error_code'], req_content['error'],
                                                                metadata).encode('utf8')
        raise DmsMetadataError(msg)
    response_id = req_content['id']

    upload_url = 'http://{ws[host]}:{ws[port]}/file_upload/{ws[version]}/{id}'.format(ws=ws, id=response_id)
    files = {'filedata': ('archive.tar', tar_content, 'application/tar', {'Expires': '0'})}
    upload_req = requests.post(upload_url, auth=auth, files=files)
    req_content = json.loads(upload_req.content)
    if not req_content['success']:
        msg = u"code: '{}', error: '{}'".format(req_content['error_code'], req_content.get('error') or
                                                req_content['message']).encode('utf8')
        raise FileUploadError(msg)

    next_id_txt = str(next_id) if six.PY3 else str(next_id).decode()
    next_id_path.write_text(next_id_txt)


def process_mails():
    arguments = docopt(__doc__)
    config = configparser.ConfigParser()
    config_file = arguments["FILE"]
    config.read(config_file)

    host, port, ssl, login, password = get_mailbox_infos(config)
    counter_dir = Path(config["webservice"]["counter_dir"])
    counter_dir.mkdir(exist_ok=True)
    lock_filepath = counter_dir / "lock_{0}".format(config['webservice']['client_id'])
    lock = zc.lockfile.LockFile(lock_filepath.as_posix())

    handler = IMAPEmailHandler()
    handler.connect(host, port, ssl, login, password)

    if arguments.get("--requeue_errors"):
        amount = handler.reset_errors()
        logger.info("{} emails in error were put back in waiting state".format(amount))
        handler.disconnect()
        lock.close()
        sys.exit()

    imported = errors = unsupported = 0
    for mail_info in handler.get_waiting_emails():
        mail_id = mail_info.id
        mail = mail_info.mail
        pdf_path = get_preview_pdf_path(config, mail_id)
        try:
            parser = Parser(mail)
            if parser.origin == 'Generic inbox':
                mail_sender = parser.headers["From"][0][1]
                notify_unsupported_origin(config, mail, mail_sender)
                handler.mark_mail_as_unsupported(mail_id)
                unsupported += 1
                continue
            headers = parser.headers
            attachments = parser.attachments
            parser.generate_pdf(pdf_path)
            send_to_ws(config, headers, pdf_path, attachments)
            handler.mark_mail_as_imported(mail_id)
            imported += 1
        except Exception as e:
            logger.error(e, exc_info=True)
            notify_exception(config, mail, e)
            handler.mark_mail_as_error(mail_id)
            errors += 1

    logger.info(
        "{} emails have been imported. {} email are unsupported. {} emails have caused an error.".format(
            imported, unsupported, errors
        )
    )
    handler.disconnect()
    lock.close()
