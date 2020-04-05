# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function, division

import os
from functools import lru_cache
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SSH_CATEGORYS_SET = set([
    'education, media & information science',
    'sociology & anthropology',
    'community & social issues',
    'business, economics, planning',
    'political science & administration',
    'law',
    'special psychiatry',
])


@lru_cache(maxsize=None)
def _get_wc_ecoom_map_lower():
    df_ecoom_category = pd.read_excel(os.path.join(BASE_DIR, 'configs/ecoom_category_20190806.xlsx'))
    wc_ecoom_map = {row['WC']: row['ECOOM'] for i, row in df_ecoom_category.iterrows()}
    wc_ecoom_map_lower = {k.lower().strip(): v.lower().strip() for k, v in wc_ecoom_map.items()}
    return wc_ecoom_map_lower


def parse_ecoom_categorys(row, field='WC'):
    wc_ecoom_map_lower = _get_wc_ecoom_map_lower()
    wcs = str(row.get(field, '')).split(';')
    ecooms = []
    for wc in wcs:
        wc = wc.strip().lower()
        wc1 = wc.replace('&', 'and')
        if wc in wc_ecoom_map_lower:
            ecooms.append(wc_ecoom_map_lower[wc])
        elif wc1 in wc_ecoom_map_lower:
            ecooms.append(wc_ecoom_map_lower[wc1])
        else:
            ecooms.append(wc)
    return ';'.join(ecooms).lower()
