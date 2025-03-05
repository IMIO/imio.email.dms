from docopt import docopt
from imio.email.dms.imap import MailData
from imio.email.dms.main import __doc__
from imio.email.dms.main import clean_mails
from imio.email.dms.main import compress_pdf
from imio.email.dms.main import modify_attachments
from imio.email.dms.main import Notify
from imio.email.dms.main import process_mails
from imio.email.dms.main import resize_inline_images
from imio.email.parser import email_policy  # noqa
from imio.email.parser.parser import Parser
from imio.email.parser.tests import test_parser
from imio.email.parser.tests.test_parser import get_eml_message
from pathlib import Path
from unittest.mock import patch

import configparser
import email
import os
import PyPDF2
import tarfile
import unittest


TEST_FILES_PATH = os.path.join(os.path.dirname(__file__), "files")
EML_TEST_FILES_PATH = os.path.join(os.path.dirname(test_parser.__file__), "files")


class TestMain(unittest.TestCase):
    def setUp(self):
        self.config = configparser.ConfigParser()

    def test_modify_attachments(self):
        to_tests = [
            {
                "fn": "01_email_with_inline_and_annexes.eml",
                "orig": {"nb": 4, "len": [269865, 673, 9309, 310852]},
                "mod": {"all_nb": 4, "at_nb": 2, "len": [186946, 673, 9309, 154746], "mod": [True, None, None, True]},
            },
            {
                "fn": "04_email_with_pdf_attachment.eml",
                "orig": {"nb": 1, "len": [2231999]},
                "mod": {"all_nb": 1, "at_nb": 1, "len": [160175], "mod": [True]},
            },
        ]
        # breakpoint()
        for dic in to_tests:
            name = dic["fn"]
            eml = get_eml_message(name)
            parser = Parser(eml, False, name)
            self.assertEqual(len(parser.attachments), dic["orig"]["nb"])
            self.assertListEqual([at["len"] for at in parser.attachments], dic["orig"]["len"])
            mod_attach = modify_attachments(name, parser.attachments)
            self.assertEqual(len(mod_attach), dic["mod"]["all_nb"])
            self.assertListEqual([at["len"] for at in mod_attach], dic["mod"]["len"])
            self.assertListEqual([at.get("modified") for at in mod_attach], dic["mod"]["mod"])
            mod_attach = modify_attachments(name, parser.attachments, with_inline=False)
            self.assertEqual(len(mod_attach), dic["mod"]["at_nb"])

    def test_compress_pdf(self):
        pdf_file = os.path.join(TEST_FILES_PATH, "pdf-example-bookmarks-1-2.pdf")
        with open(pdf_file, "rb") as pdf:
            pdf_content = pdf.read()
        compressed_pdf_content = compress_pdf(pdf_content)
        self.assertGreater(len(pdf_content), len(compressed_pdf_content))

        with open("pdf-example-bookmarks-1-2-compressed.pdf", "wb") as f:
            f.write(compressed_pdf_content)

        with open("pdf-example-bookmarks-1-2-compressed.pdf", "rb") as f:
            reader = PyPDF2.PdfFileReader(f)
            self.assertFalse(reader.getIsEncrypted())
            self.assertEqual(reader.getNumPages(), 2)
            self.assertEqual(reader.getDocumentInfo().get("/Producer"), "GPL Ghostscript 10.02.1")

    def test_resize_inline_images(self):
        def get_html_part(message):
            for part in message.walk():
                if part.get_content_type() == "text/html":
                    return part
            return None

        to_tests = [
            {
                "fn": "01_email_with_inline_and_annexes.eml",
                "orig": {
                    "html_parts": ['<img src="cid:ii_m5kspqrb0" alt="2-1-page-daccueil.png" width="1920" height="953">']
                },
                "mod": {
                    "html_parts": [
                        '<img alt="2-1-page-daccueil.png" height="953" src="cid:ii_m5kspqrb0" style="max-width: 100%; height: auto; width: auto" width="1920"/>'
                    ]
                },
            },
            {
                "fn": "02_email_with_inline_annex_eml.eml",
                "orig": {
                    "html_parts": ['<img src="cid:ii_m5kuur6b1" alt="organization_icon.png" width="16" height="16">']
                },
                "mod": {
                    "html_parts": ['<img src="cid:ii_m5kuur6b1" alt="organization_icon.png" width="16" height="16">']
                },
            },
            {
                "fn": "03_email_with_false_inline.eml",
                "orig": {"html_parts": []},
                "mod": {"html_parts": []},
            },
            {
                "fn": "04_email_with_pdf_attachment.eml",
                "orig": {"html_parts": []},
                "mod": {"html_parts": []},
            },
        ]

        for dic in to_tests:
            mail_name = dic["fn"]
            eml = get_eml_message(mail_name)
            parser = Parser(eml, False, mail_name)

            attachments = modify_attachments(mail_name, parser.attachments, with_inline=True)
            new_message = resize_inline_images(mail_name, parser.message, attachments)
            new_parser = Parser(new_message, False, mail_name, extract=False)

            self.assertEqual(len(new_parser.attachments), len(parser.attachments))
            self.assertGreaterEqual(len(parser.message.as_string()), len(new_message.as_string()))

            for old_at, new_at in zip(attachments, new_parser.attachments):
                if old_at["disp"] != "inline":
                    continue
                self.assertGreaterEqual(old_at["len"], new_at["len"])

            for i in range(len(dic["orig"]["html_parts"])):
                old_html_part = dic["orig"]["html_parts"][i]
                new_html_part = dic["mod"]["html_parts"][i]
                self.assertIn(
                    old_html_part,
                    get_html_part(parser.message).get_content(),
                )
                self.assertIn(
                    new_html_part,
                    get_html_part(new_message).get_content(),
                )

    def test_process_mails_help(self):
        with self.assertRaises(SystemExit):
            docopt(__doc__, argv=["--help"])

    @patch("imio.email.dms.main.dev_mode", True)
    def test_process_mails_test_eml(self):
        to_test = [
            {
                "filename": "01_email_with_inline_and_annexes.eml",
                "expected_exit_code": None,
            },
            {
                "filename": "02_email_with_inline_annex_eml.eml",
                "expected_exit_code": None,
            },
            {
                "filename": "03_email_with_false_inline.eml",
                "expected_exit_code": None,
            },
            {
                "filename": "04_email_with_pdf_attachment.eml",
                "expected_exit_code": None,
            },
            {
                "filename": "eml_file_that_does_not_exist.eml",
                "expected_exit_code": 0,
            },
        ]

        for dic in to_test:
            filename = dic["filename"]
            expected_exit_code = dic["expected_exit_code"]
            with patch("sys.argv", ["main.py", "../../config.ini", f"--test_eml={EML_TEST_FILES_PATH}/{filename}"]):
                with patch("imio.email.dms.main.IMAPEmailHandler"):
                    with self.assertRaises(SystemExit) as cm:
                        process_mails()
            self.assertEqual(cm.exception.code, expected_exit_code)

    @patch("imio.email.dms.main.dev_mode", True)
    def test_process_mails_get_eml(self):
        with patch("sys.argv", ["main.py", "../../config.ini", "--get_eml=01"]):
            with patch("imio.email.dms.main.IMAPEmailHandler") as MockIMAPEmailHandler:
                with self.assertRaises(SystemExit) as cm:
                    mock_handler = MockIMAPEmailHandler.return_value
                    mock_handler.get_mail.return_value = get_eml_message("01_email_with_inline_and_annexes.eml")
                    process_mails()
        self.assertIsNone(cm.exception.code)

        with (
            open(os.path.join(EML_TEST_FILES_PATH, "01_email_with_inline_and_annexes.eml"), "r") as original_file,
            open("01.eml", "r") as output_file,
        ):
            # ipdb.set_trace()
            original_mail = Parser(
                email.message_from_file(original_file, policy=email_policy),
                False,
                "01",
            )
            output_mail = Parser(
                email.message_from_file(output_file, policy=email_policy),
                False,
                "01",
                extract=False,
            )
            self.assertEqual(original_mail.parsed_message.body, output_mail.parsed_message.body)
            self.assertEqual(original_mail.parsed_message.headers, output_mail.parsed_message.headers)
            self.assertEqual(original_mail.parsed_message.attachments, output_mail.parsed_message.attachments)

    @patch("imio.email.dms.main.dev_mode", True)
    def test_process_mails_gen_pdf(self):
        with patch("sys.argv", ["main.py", "../../config.ini", "--gen_pdf=01"]):
            with patch("imio.email.dms.main.IMAPEmailHandler") as MockIMAPEmailHandler:
                with self.assertRaises(SystemExit) as cm:
                    mock_handler = MockIMAPEmailHandler.return_value
                    mock_handler.get_mail.return_value = get_eml_message("01_email_with_inline_and_annexes.eml")
                    process_mails()
        self.assertIsNone(cm.exception.code)
        self.assertTrue(Path("/tmp/01.pdf").exists())

    @patch("imio.email.dms.main.dev_mode", True)
    @patch("imio.email.dms.utils.dev_mode", True)
    def test_process_mails_no_option(self):
        with patch("sys.argv", ["main.py", "../../config.ini"]):
            with patch("imio.email.dms.main.IMAPEmailHandler") as MockIMAPEmailHandler:
                with self.assertRaises(SystemExit) as cm:
                    mock_handler = MockIMAPEmailHandler.return_value
                    mock_handler.get_waiting_emails.return_value = [
                        MailData("01", get_eml_message("01_email_with_inline_and_annexes.eml")),
                        MailData("02", get_eml_message("02_email_with_inline_annex_eml.eml")),
                        MailData("03", get_eml_message("03_email_with_false_inline.eml")),
                        MailData("04", get_eml_message("04_email_with_pdf_attachment.eml")),
                    ]
                    process_mails()

        self.assertIsNone(cm.exception.code)

        self.assertTrue(Path("/tmp/01Z999900000001.tar").exists())
        with tarfile.open("/tmp/01Z999900000001.tar", "r") as f:
            self.assertEqual(len(f.getnames()), 4)
            self.assertEqual(
                f.getnames(),
                [
                    "email.pdf",
                    "metadata.json",
                    "/attachments/accuse.odt",
                    "/attachments/Capture du 2016-12-12 10-56-00-(redimensionné).png",
                ],
            )

        self.assertTrue(Path("/tmp/01Z999900000002.tar").exists())
        with tarfile.open("/tmp/01Z999900000002.tar", "r") as f:
            self.assertEqual(len(f.getnames()), 4)
            self.assertEqual(
                f.getnames(),
                [
                    "email.pdf",
                    "metadata.json",
                    "/attachments/texte_simple ééé.txt",
                    "/attachments/Email avec inline et annexe.eml",
                ],
            )

        self.assertTrue(Path("/tmp/01Z999900000003.tar").exists())
        with tarfile.open("/tmp/01Z999900000003.tar", "r") as f:
            self.assertEqual(len(f.getnames()), 4)
            self.assertEqual(
                f.getnames(),
                [
                    "email.pdf",
                    "metadata.json",
                    "/attachments/Erreur 2.jpg",
                    "/attachments/Erreur 1.png",
                ],
            )

    @patch("imio.email.dms.main.dev_mode", True)
    def test_clean_mails_help(self):
        with self.assertRaises(SystemExit):
            docopt(clean_mails.__doc__, argv=["--help"])

    @patch("imio.email.dms.main.dev_mode", True)
    def test_clean_mails_list_only(self):
        emails = {
            "01": get_eml_message("01_email_with_inline_and_annexes.eml"),
            "02": get_eml_message("02_email_with_inline_annex_eml.eml"),
            "03": get_eml_message("03_email_with_false_inline.eml"),
            "04": get_eml_message("04_email_with_pdf_attachment.eml"),
        }
        with (
            patch("sys.argv", ["main.py", "../../config.ini", "--list_only"]),
            patch("imio.email.dms.main.IMAPEmailHandler") as MockIMAPEmailHandler,
            self.assertRaises(SystemExit) as cm,
        ):
            mock_handler = MockIMAPEmailHandler.return_value
            mock_handler.connection.search.return_value = ("OK", ["01 02 03 04"])
            mock_handler.connection.fetch.return_value = ("OK", [b""])
            mock_handler.get_email.side_effect = lambda x: emails[x]
            clean_mails()

    @patch("imio.email.dms.main.Notify._send")
    def test_notify_exception(self, notify_send):
        def assert_msg(msg):
            with open(f"/tmp/{msg['Subject']}.eml", "w") as f:
                f.write(msg.as_string())

        notify_send.side_effect = assert_msg

        msg = get_eml_message("01_email_with_inline_and_annexes.eml")
        parser = Parser(msg, False, "01")
        config = configparser.ConfigParser()
        config.read("../../config.ini")
        try:
            raise Exception("Test exception")
        except Exception as e:
            Notify(parser.message, config, parser.headers).exception("01", e)

        # Assert msg to support
        with open("/tmp/Error handling an email for client 019999.eml", "r") as f:
            msg = email.message_from_file(f)
        self.assertEqual(msg["Subject"], "Error handling an email for client 019999")
        self.assertEqual(msg["From"], "imio.email.dms@imio.be")
        self.assertEqual(msg["To"], "support-docs@imio.be")
        self.assertEqual(
            msg.get_payload(0).get_payload(),
            "\nProblematic mail is attached.\n\nClient ID : 019999\nIMAP login : \n\nmail id : 01\n\nCorresponding exception : <class 'Exception'>\nTest exception\n\n\n\n",
        )
        self.assertEqual(msg.get_payload(1).get_content_type(), "message/rfc822")
        self.assertEqual(msg.get_payload(1)["Content-Disposition"], "inline")

        # Assert msg to client
        with open("/tmp/Erreur dans le traitement du mail transféré vers iA.Docs.eml", "r") as f:
            msg = email.message_from_file(f)
        self.assertEqual(
            msg["Subject"], "=?utf-8?q?Erreur_dans_le_traitement_du_mail_transf=C3=A9r=C3=A9_vers_iA=2EDocs?="
        )
        self.assertEqual(msg["From"], "imio.email.dms@imio.be")
        self.assertEqual(msg["To"], "stephan.mio@mail.be")
        self.assertEqual(msg.get_payload(1).get_content_type(), "message/rfc822")
        self.assertEqual(msg.get_payload(1)["Content-Disposition"], "inline")

    @patch("imio.email.dms.main.Notify._send")
    def test_notify_unsupported_origin(self, notify_send):
        def assert_msg(msg):
            self.assertEqual(msg["Subject"], "Erreur de transfert de votre email dans iA.Docs")
            self.assertEqual(msg["From"], "imio.email.dms@imio.be")
            self.assertEqual(msg["To"], "stephan.perso@mail.be")
            self.assertEqual(msg.get_payload(1).get_content_type(), "message/rfc822")
            self.assertEqual(msg.get_payload(1)["Content-Disposition"], "inline")

        notify_send.side_effect = assert_msg

        msg = get_eml_message("01_email_with_inline_and_annexes.eml")
        parser = Parser(msg, False, "01")
        config = configparser.ConfigParser()
        config.read("../../config.ini")
        Notify(parser.message, config, parser.headers).unsupported_origin()

    @patch("imio.email.dms.main.Notify._send")
    def test_notify_ignored(self, notify_send):
        def assert_msg(msg):
            self.assertEqual(msg["Subject"], "Transfert non autorisé de stephan.mio@mail.be pour le client 019999")
            self.assertEqual(msg["From"], "imio.email.dms@imio.be")
            self.assertEqual(msg["To"], "stephan.mio@mail.be")
            self.assertEqual(msg["Bcc"], "support-docs@imio.be")
            # self.assertEqual(msg["Bcc"], "support-docs@imio.be")
            self.assertEqual(msg.get_payload(1).get_content_type(), "message/rfc822")
            self.assertEqual(msg.get_payload(1)["Content-Disposition"], "inline")

        notify_send.side_effect = assert_msg

        msg = get_eml_message("01_email_with_inline_and_annexes.eml")
        parser = Parser(msg, False, "01")
        config = configparser.ConfigParser()
        config.read("../../config.ini")
        Notify(parser.message, config, parser.headers).ignored("01")

    @patch("imio.email.dms.main.Notify._send")
    def test_notify_result(self, notify_send):
        def assert_msg(msg):
            self.assertEqual(msg["Subject"], "Result of clean_mails for client 019999")
            self.assertEqual(msg["From"], "imio.email.dms@imio.be")
            self.assertEqual(msg["To"], "support-docs@imio.be")
            self.assertIn("Some message", msg.get_payload(0).get_payload())

        notify_send.side_effect = assert_msg

        msg = get_eml_message("01_email_with_inline_and_annexes.eml")
        parser = Parser(msg, False, "01")
        config = configparser.ConfigParser()
        config.read("../../config.ini")
        Notify(parser.message, config, parser.headers).result("Result of clean_mails", "Some message")
