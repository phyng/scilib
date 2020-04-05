# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function, division


def parse_is_article(row):
    if 'article' in str(row['DT']).lower():
        return True
    return False


def parse_is_oa(row):
    oa = str(row.get('OA', '')).lower()
    if oa and oa != 'nan':
        return True
    return False