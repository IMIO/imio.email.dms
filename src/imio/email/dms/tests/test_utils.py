# -*- coding: utf-8 -*-

from imio.email.dms.utils import get_reduced_size
from imio.email.dms.utils import safe_unicode
from imio.email.dms.utils import save_as_eml
from imio.email.dms.utils import reception_date
from imio.email.dms.utils import get_next_id
from imio.email.dms.utils import get_unique_name
from imio.email.dms.utils import set_next_id

import unittest

from email import message_from_file
import os


class TestUtils(unittest.TestCase):
    def setUp(self):
        self.current_file_path = os.path.abspath(__file__)
        self.current_dir = os.path.dirname(self.current_file_path)
        self.eml_path_0 = os.path.join(self.current_dir, "../tests/files/0_simple_eml.eml") # noqa
        self.eml_path_1 = os.path.join(self.current_dir, "../tests/files/01_email_containing_eml.eml") # noqa
        self.eml_path_2 = os.path.join(self.current_dir, "../tests/files/02_email_containing_eml_containing_eml.eml")# noqa
        self.output_path = os.path.join(self.current_dir, "../tests/files/output.eml") # noqa

    def test_get_reduced_size(self):
        self.assertTupleEqual((False, None), get_reduced_size((500, 500), 600))
        self.assertTupleEqual((True, (400, 400)), get_reduced_size((500, 500), 400))
        self.assertTupleEqual((True, (400, 333)), get_reduced_size((600, 500), 400))
        self.assertTupleEqual((True, (300, 400)), get_reduced_size((600, 800), 400))

    def test_safe_unicode(self):
        self.assertTrue(safe_unicode("test") == "test")
        self.assertTrue(safe_unicode("test", "utf-8") == "test")
        self.assertFalse(safe_unicode("test", "UFT-9") == "test")
        self.assertFalse(safe_unicode(8) == "test")
        with self.assertRaises(TypeError):
            safe_unicode(8)

    def test_save_as_eml(self):
        with open(self.eml_path_0, "r") as file:
            message = message_from_file(file)

        save_as_eml(self.output_path, message)

        with open(self.output_path, "r") as file:
            output_message = message_from_file(file)
            # breakpoint()

        self.assertEqual(message.as_string(), output_message.as_string())
        # self.assertEqual(message.get_payload(), output_message.get_payload())
        # self.assertEqual(message.items(), output_message.items())

        os.remove(self.output_path)

    def test_reception_date(self):
        with open(self.eml_path_0, "r") as file:
            message = message_from_file(file)

        # La date présente dans l'eml est correctement formatée
        self.assertTrue(reception_date(message) == "2023-03-27 16:00", f"Expected '2023-03-27 16:00' but got '{reception_date(message)}'") # noqa

        # Pas de date dans l'eml
        del message["Date"]
        self.assertFalse(reception_date(message) != "")

        # Format de date incorrect
        message["Date"] = "Invalid Date"
        self.assertFalse(reception_date(message) != "")

    def test_get_next_id(self):
        pass

    def test_get_unique_name(self):
        pass

    def test_set_next_id(self):
        pass
