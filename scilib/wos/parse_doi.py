# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function, division


def parse_cr_dois(row):
    tokens = str(row.get('CR', '')).split()
    items = [i.strip(';') for i in tokens if i.startswith('10.')]
    return ';'.join(items)
