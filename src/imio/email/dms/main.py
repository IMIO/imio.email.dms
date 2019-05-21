# -*- coding: utf-8 -*-

"""
Usage: process_mails [-h] FILE

Arguments:
    FILE         config file

Options:
    -h --help
"""
from datetime import datetime
from docopt import docopt
from hashlib import md5
from io import BytesIO
from imio.email.dms.fetcher import IMAPEmailFetcher
from imio.email.parser.parser import Parser
from pathlib import Path
import configparser
import json
import os
import requests
import tarfile
import zc.lockfile


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
    upload_req = requests.post(upload_url,
                               auth=auth,
                               data={"filedata": tar_content})

    external_id_path.write_text(str(external_id))


def process_mails():
    arguments = docopt(__doc__)
    config = configparser.ConfigParser()
    config_file = arguments["FILE"]
    config.read(config_file)

    host, port, ssl, login, password = get_mailbox_infos(config)
    lock = zc.lockfile.LockFile("lock_{0}".format(config['webservice']['client_id']))
    fetcher = IMAPEmailFetcher()
    fetcher.connect(host, port, ssl, login, password)

    for mail_info in fetcher.get_unread_emails():
        mail_id = mail_info.id
        mail = mail_info.mail
        pdf_path = get_preview_pdf_path(config, mail_id)
        try:
            parser = Parser(mail)
            headers = parser.headers
            print(headers)
            attachments = parser.attachments
            print([a['filename'] for a in attachments])
            parser.generate_pdf(pdf_path)
            send_to_ws(config, headers, pdf_path, attachments)
            fetcher.mark_mail_as_read(mail_id)
        except:
            fetcher.mark_mail_as_error(mail_id)
    fetcher.disconnect()
    lock.close()
