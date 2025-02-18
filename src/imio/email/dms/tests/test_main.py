from docopt import docopt
from imio.email.dms.main import __doc__
from imio.email.dms.main import compress_pdf
from imio.email.dms.main import modify_attachments
from imio.email.dms.main import process_mails
from imio.email.dms.main import resize_inline_images
from imio.email.parser.parser import Parser
from imio.email.parser.tests.test_parser import get_eml_message
from parameterized import parameterized
from unittest.mock import patch

import configparser
import os
import unittest


TEST_FILES_PATH = "../../src/imio/email/dms/tests/files"
EML_TEST_FILES_PATH = "../../devel/imio.email.parser/src/imio/email/parser/tests/files"


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

        # TODO test compressed_pdf_content is a valid pdf

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

    @parameterized.expand(
        [
            (
                [
                    "main.py",
                    "../../config.ini.dev",
                    f"--test_eml={EML_TEST_FILES_PATH}/01_email_with_inline_and_annexes.eml",
                ],
                None,  # None means no error, 0 means error
            ),
            (
                [
                    "main.py",
                    "../../config.ini.dev",
                    f"--test_eml={EML_TEST_FILES_PATH}/02_email_with_inline_annex_eml.eml",
                ],
                None,
            ),
            (
                [
                    "main.py",
                    "../../config.ini.dev",
                    f"--test_eml={EML_TEST_FILES_PATH}/03_email_with_false_inline.eml",
                ],
                None,
            ),
            (
                [
                    "main.py",
                    "../../config.ini.dev",
                    f"--test_eml={EML_TEST_FILES_PATH}/04_email_with_pdf_attachment.eml",
                ],
                None,
            ),
            (
                [
                    "main.py",
                    "../../config.ini.dev",
                    f"--test_eml={EML_TEST_FILES_PATH}/eml_file_that_does_not_exist.eml",
                ],
                0,
            ),
        ]
    )
    def test_main_test_eml(self, args, expected_exit_code):
        with patch("sys.argv", args):
            with self.assertRaises(SystemExit) as cm:
                process_mails()
        self.assertEqual(cm.exception.code, expected_exit_code)
        # TODO add more asserts

    def test_main_help(self):
        with self.assertRaises(SystemExit):  # docopt exits when --help is passed
            docopt(__doc__, argv=["--help"])
