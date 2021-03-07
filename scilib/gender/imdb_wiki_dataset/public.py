# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function, division

import os
import pandas as pd

BASE_DIR = os.path.dirname(__file__)
WIKI_GENDER_TEST_CSV_PATH = os.path.join(BASE_DIR, 'data/wiki_gender_test.csv')


def load_test_data():
    items = [dict(item) for index, item in pd.read_csv(WIKI_GENDER_TEST_CSV_PATH).iterrows()]
    return list(({item['name']: item for item in items}).values())
