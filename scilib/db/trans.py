# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function, division

import csv
from .es import index_or_update_rows

""" Data Trans

- pgcsv: PostgreSQL export csn with headers
- items
- es
- ndjson
"""


def pgcsv_to_items(csv_path):
    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        headers = next(reader, None)
        items = []
        for row in reader:
            item = {h: v for h, v in zip(headers, row)}
            items.append(item)
    return items


def items_to_es(items, es_index, es_pk):
    index_or_update_rows(items, index=es_index, pk=es_pk)


def pgcsv_to_es(csv_path, es_index, es_pk):
    items = pgcsv_to_items(csv_path)
    items_to_es(items, es_index, es_pk)
