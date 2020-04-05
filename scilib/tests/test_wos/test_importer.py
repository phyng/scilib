# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function, division

import os
from unittest import TestCase
from wos.importer import read_text_format_dir, read_text_format_dir_as_pd


class WOSImporterTest(TestCase):

    def test_read_text_format_dir(self):
        dir_path = os.path.dirname(__file__)
        items = list(read_text_format_dir(dir_path))

        self.assertEqual(len(items), 500)
        for item in items:
            for key in item.keys():
                self.assertEqual(len(key), 2)
            self.assertTrue(item['UT'].startswith('WOS:'))

    def test_read_text_format_dir_as_pd(self):
        dir_path = os.path.dirname(__file__)
        df = read_text_format_dir_as_pd(dir_path)

        self.assertEqual(df.shape[0], 500)
