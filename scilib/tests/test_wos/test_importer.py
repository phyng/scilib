# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function, division

import os
import asyncio
from unittest import TestCase

from scilib.wos.importer import read_text_format_dir, read_text_format_dir_as_pd, get_uts_parallel

TEST_PATH = os.path.dirname(__file__)


class WOSImporterTest(TestCase):

    def test_read_text_format_dir(self):
        items = list(read_text_format_dir(TEST_PATH))

        self.assertEqual(len(items), 500)
        for item in items:
            for key in item.keys():
                self.assertEqual(len(key), 2)
            self.assertTrue(item['UT'].startswith('WOS:'))

    def test_read_text_format_dir_as_pd(self):
        df = read_text_format_dir_as_pd(TEST_PATH)
        self.assertEqual(df.shape[0], 500)

    def test_get_uts_parallel(self):
        uts = asyncio.run(get_uts_parallel(TEST_PATH))
        self.assertEqual(len(uts), 500)
