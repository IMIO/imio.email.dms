# -*- coding: utf-8 -*-

from imio.email.dms import dev_mode
from imio.email.dms.utils import get_next_id
from imio.email.dms.utils import get_reduced_size
from imio.email.dms.utils import set_next_id
from unittest.mock import patch

import configparser
import unittest


class TestUtils(unittest.TestCase):
    def test_get_reduced_size(self):
        self.assertTupleEqual((False, (500, 500)), get_reduced_size((500, 500), (None, None)))
        self.assertTupleEqual((False, (500, 500)), get_reduced_size((500, 500), (600, None)))
        self.assertTupleEqual((True, (400, 400)), get_reduced_size((500, 500), (400, 450)))
        self.assertTupleEqual((True, (400, 333)), get_reduced_size((600, 500), (400, None)))
        self.assertTupleEqual((True, (300, 400)), get_reduced_size((600, 800), (None, 400)))

    def test_next_id(self):
        config = configparser.ConfigParser()
        config.read("../../config.ini.dev")

        devinfos = {"nid": None}
        with patch("imio.email.dms.dev_mode", True):
            set_next_id(config, 0)
            self.assertTupleEqual((1, "01Z9996"), get_next_id(config, devinfos))
            self.assertTupleEqual((2, "01Z9996"), get_next_id(config, devinfos))
            self.assertTupleEqual((3, "01Z9996"), get_next_id(config, devinfos))

        # devinfos = {"nid": None}
        # with patch("imio.email.dms.dev_mode", False):
        #     set_next_id(config, 0)
        #     self.assertTupleEqual((1, "01Z9996"), get_next_id(config, devinfos))
        #     self.assertTupleEqual((1, "01Z9996"), get_next_id(config, devinfos))
        #     self.assertTupleEqual((1, "01Z9996"), get_next_id(config, devinfos))

        # FIXME check why patch doesn't work here
