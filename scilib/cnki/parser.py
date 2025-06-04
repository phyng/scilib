# coding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import datetime
import re
import pandas as pd
from pathlib import Path

from libs.iterlib import uniqify

CLC_MAP_DEFAULT_PATH = Path(__file__).parent / 'config/clc_map.csv'
CNKI_FIELDS = [
    'SrcDatabase',
    'Title',
    'Author',
    'Organ',
    'Source',
    'Keyword',
    'Summary',
    'PubTime',
    'FirstDuty',
    'Fund',
    'Year',
    'Volume',
    'Period',
    'PageCount',
    'CLC',
    'ISSN',
    'CN',
    'CF',
    'DFR',
    'RFN',
    'DOI',
]


def get_clc_map(*, clc_map_path=CLC_MAP_DEFAULT_PATH):
    clc_map_data = {}
    for _, row in pd.read_csv(clc_map_path, encoding='utf-8').iterrows():
        if row['key'] and str(row['key']) != 'nan' and row['value'] and str(row['value']) != 'nan':
            clc_map_data[row['key'].strip()] = row['value'].strip()
    return clc_map_data


def parse_fu_tokens(row):
    if row.get('Fund', '') and str(row['Fund']) != 'nan':
        tokens = [re.sub(r'[^a-zA-Z0-9]', '', i) for i in re.split(r'[^a-zA-Z0-9]', row['Fund'])]
        return list(uniqify([i for i in tokens if i]))
    return []


def parse_clc_tokens(row):
    if row.get('CLC', '') and str(row['CLC']) != 'nan':
        clc = row['CLC']
        try:
            clc = clc[:clc.index('ISSN')]
        except ValueError:
            pass
        return [i.strip() for i in clc.split(';') if i.strip()]
    return []


def parse_clc_level1_tokens(item, clc_map):
    tokens = []
    for token in item['clc_tokens']:
        if not token:
            continue
        elif token in ['+']:
            continue
        elif token[:1] in clc_map:
            tokens.append(token[:1])
        else:
            pass
    return list(uniqify(tokens))


def parse_clc_level2_tokens(item, clc_map):
    tokens = []
    for token in item['clc_tokens']:
        if not token:
            continue
        elif token in ['+']:
            continue
        elif token[:2] in clc_map:
            tokens.append(token[:2])
        elif token[:3] in clc_map:
            tokens.append(token[:3])
        else:
            pass  # tokens.append(token)
    return list(uniqify(tokens))


def parse_keyword_tokens(item, keyword_field='Keyword', keyword_replace_map=None):
    keyword = item.get(keyword_field, '') or ''
    if str(keyword) == 'nan':
        return []
    tokens = re.split(r'[,;，]', keyword)
    tokens = [(keyword_replace_map or {}).get(i.strip(), i.strip()) for i in tokens if i and i.strip()]
    tokens = list(uniqify(tokens))
    return tokens


def parse_year(item, year_field='Year'):
    year = item.get(year_field, '') or ''
    if not year or str(year) == 'nan':
        return None
    try:
        if len(str(int(year))) == 4:
            return int(year)
    except (ValueError, TypeError):
        pass
    return None


def parse_list_date(list_date):
    try:
        list_date = list_date.split()[0]
        tokens = list_date.split('-')
        y = int(tokens[0])
        m = int(tokens[1])
        d = int(tokens[2])
        return datetime.date(y, m, d).strftime(r'%Y-%m-%d')
    except Exception:
        return None


def parse_cnki_item(item, clc_map, keyword_replace_map):
    item['fu_tokens'] = parse_fu_tokens(item)
    item['keyword_tokens'] = parse_keyword_tokens(item, keyword_replace_map=keyword_replace_map)
    item['parsed_year'] = parse_year(item)
    item['clc_tokens'] = parse_clc_tokens(item)
    item['clc_level1_tokens'] = parse_clc_level1_tokens(item, clc_map=clc_map)
    item['clc_level2_tokens'] = parse_clc_level2_tokens(item, clc_map=clc_map)
