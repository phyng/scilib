# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function, division

import os
import re
from functools import lru_cache, partial
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COUNTRY_MAP = {
    "England": "UK",
    "Scotland": "UK",
    "Wales": "UK",
}
HMT_MAP = {
    'hong kong': ['hong kong', 'hongkong'],
    'macao': ['macao', 'macau'],
}


@lru_cache(maxsize=None)
def _get_std_country_list():
    df_std_country = pd.read_excel(os.path.join(BASE_DIR, 'configs/std_country_map.xlsx'))
    return [
        {'end': row['end'].lower().strip().replace('#', ' '), 'country': row['country'].lower().strip()}
        for i, row in df_std_country.iterrows()
    ]


def parse_country(
    row,
    *,
    field='C1',
    extra_field=None,
    hmt=False,
):
    std_country_list = _get_std_country_list()
    address_list = str(row.get(field, ''))
    if extra_field:
        address_list += ';'
        address_list += str(row.get(extra_field, ''))
    address_list = re.sub(r'\[.*?\]', '', address_list)
    address_list = address_list.split(';')
    countrys = []
    nomatchs = []

    for address in address_list:
        address = address.replace('.', '').lower()
        if address == 'nan':
            continue

        # hmt
        try:
            for key, tokens in HMT_MAP.items():
                for token in tokens:
                    if token in address:
                        if hmt:
                            countrys.append(key)
                        else:
                            countrys.append('china')
                        raise StopIteration('match')
        except StopIteration:
            continue

        country_list = re.split(' |,', address)
        country_list_join = ' '.join(country_list)
        for row in std_country_list:
            if country_list_join.endswith(row['end']):
                parsered_country = row['country']
                countrys.append(parsered_country)
                break
        else:
            if re.search(r'[a-z]{2} \d{5}$', address):
                countrys.append('usa')
            elif re.search('(xiamen|china)', address):
                countrys.append('china')
            elif re.match(r'^[a-z]+, *[a-z]+$', address.strip()):
                continue
            else:
                nomatchs.append(address)

    return ';'.join(countrys)


def add_countrys_to_df(
    df_temp,
    *,
    field='C1',
    extra_field=None,
    hmt=False,
):
    _apply_col = partial(parse_country, field=field, extra_field=extra_field, hmt=hmt)
    return df_temp.apply(_apply_col, axis=1)
