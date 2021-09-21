# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function, division

import os
import pandas as pd

BASE_DIR = os.path.dirname(__file__)
DATASETS = {
    'wiki': os.path.join(BASE_DIR, 'data/wiki_gender_test.csv'),
    'usa': os.path.join(BASE_DIR, 'data/usa.csv'),
}


def load_test_data(dataset='wiki'):
    items = [dict(item) for index, item in pd.read_csv(DATASETS[dataset]).iterrows()]
    return list(({item['name']: item for item in items}).values())
