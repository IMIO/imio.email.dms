# -*- coding: utf-8 -*-

from imio.email.dms.utils import get_next_id
from imio.email.dms.utils import get_reduced_size
from imio.email.dms.utils import reception_date
from imio.email.dms.utils import safe_text
from imio.email.dms.utils import save_attachment
from imio.email.dms.utils import set_next_id
from imio.email.parser.parser import Parser
from imio.email.parser.tests.test_parser import get_eml_message
from pathlib import Path
from unittest.mock import patch

import configparser
import unittest


class TestUtils(unittest.TestCase):
    def test_safe_text(self):
        test_bytes = "\u01b5".encode("utf-8")
        self.assertEqual(safe_text("spam"), "spam")
        self.assertEqual(safe_text(b"spam"), "spam")
        self.assertEqual(safe_text("spam"), "spam")
        self.assertEqual(safe_text("spam".encode("utf-8")), "spam")
        self.assertEqual(safe_text(test_bytes), "\u01b5")
        self.assertEqual(safe_text("\xc6\xb5".encode("iso-8859-1")), "\u01b5")
        self.assertEqual(safe_text(test_bytes, encoding="ascii"), "\u01b5")
        self.assertEqual(safe_text(1), 1)
        self.assertIsNone(safe_text(None))

    def test_save_attachment(self):
        email = get_eml_message("01_email_with_inline_and_annexes.eml")
        attachment = Parser(email, False, "1").attachments[0]
        folder = "/tmp"
        save_attachment(folder, attachment)

        self.assertTrue(Path(f"{folder}/2-1-page-daccueil.png").exists())
        with open("/tmp/2-1-page-daccueil.png", "rb") as file:
            self.assertEqual(file.read(), attachment["content"])

    def test_reception_date(self):
        email = get_eml_message("01_email_with_inline_and_annexes.eml")
        self.assertEqual(reception_date(email), "2025-01-06 07:51")
        email = get_eml_message("02_email_with_inline_annex_eml.eml")
        self.assertEqual(reception_date(email), "")
        email = get_eml_message("03_email_with_false_inline.eml")
        self.assertEqual(reception_date(email), "2022-02-23 15:02")
        email = get_eml_message("04_email_with_pdf_attachment.eml")
        self.assertEqual(reception_date(email), "2025-01-09 11:10")

    def test_get_reduced_size(self):
        self.assertTupleEqual((False, (500, 500)), get_reduced_size((500, 500), (None, None)))
        self.assertTupleEqual((False, (500, 500)), get_reduced_size((500, 500), (600, None)))
        self.assertTupleEqual((True, (400, 400)), get_reduced_size((500, 500), (400, 450)))
        self.assertTupleEqual((True, (400, 333)), get_reduced_size((600, 500), (400, None)))
        self.assertTupleEqual((True, (300, 400)), get_reduced_size((600, 800), (None, 400)))

    def test_next_id(self):
        config = configparser.ConfigParser()
        config.read("../../config.ini")

        devinfos = {"nid": None}
        with patch("imio.email.dms.utils.dev_mode", True):
            set_next_id(config, 0)
            self.assertTupleEqual((1, "01Z9999"), get_next_id(config, devinfos))
            self.assertTupleEqual((2, "01Z9999"), get_next_id(config, devinfos))
            self.assertTupleEqual((3, "01Z9999"), get_next_id(config, devinfos))

        devinfos = {"nid": None}
        with patch("imio.email.dms.utils.dev_mode", False):
            set_next_id(config, 0)
            self.assertTupleEqual((1, "01Z9999"), get_next_id(config, devinfos))
            self.assertTupleEqual((1, "01Z9999"), get_next_id(config, devinfos))
            self.assertTupleEqual((1, "01Z9999"), get_next_id(config, devinfos))
