# -*- coding: utf-8 -*-

from imio.email.dms.utils import get_reduced_size

import unittest


class TestUtils(unittest.TestCase):

    def test_get_reduced_size(self):
        self.assertTupleEqual((False, None), get_reduced_size((500, 500), 600))
        self.assertTupleEqual((True, (400, 400)), get_reduced_size((500, 500), 400))
        self.assertTupleEqual((True, (400, 333)), get_reduced_size((600, 500), 400))
        self.assertTupleEqual((True, (300, 400)), get_reduced_size((600, 800), 400))
