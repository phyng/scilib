# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function, division
import re
from libs.iterlib import uniqify


def parse_is_article(row):
    if 'article' in str(row.get('DT', '')).lower():
        return True
    return False


def parse_document_types(row):
    dt = str(row.get('DT', ''))
    return ';'.join([i.strip() for i in dt.split(';')])


def parse_is_oa(row):
    oa = str(row.get('OA', '')).lower()
    if oa and oa != 'nan':
        return True
    return False


def parse_py_datetime(row):
    if row.get('PY', '') and str(row['PY']) != 'nan':
        return f'{row["PY"]}-01-01'
    return None


def parse_fu_tokens(row):
    if row.get('FU', '') and str(row['FU']) != 'nan':
        tokens = [re.sub(r'[^a-zA-Z0-9]', '', i) for i in re.split(r'[^a-zA-Z0-9]', row['FU'])]
        return ';'.join(uniqify([i for i in tokens if i]))
    return ''


def parse_keyword_tokens(row, keyword_field='DE', replace_map=None):
    replace_map = replace_map or {}
    if row.get(keyword_field, '') and str(row[keyword_field]) != 'nan':
        tokens = [i.strip().lower() for i in row[keyword_field].split(';') if i and i.strip()]
        return list(uniqify([replace_map.get(i, i) for i in tokens]))
    return []
