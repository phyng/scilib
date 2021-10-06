# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function, division

import csv
import gzip
import json
from .es import index_or_update_rows

""" Data Trans

- pgcsv: PostgreSQL export csn with headers
- items
- es
- ndjson
- ndjsongz
"""


def pgcsv_to_items(csv_path, json_fields=None):
    json_fields = json_fields or []
    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        headers = next(reader, None)
        items = []
        for row in reader:
            item = {h: v for h, v in zip(headers, row)}
            for k in item.keys():
                if json_fields and k in json_fields:
                    if item[k]:
                        item[k] = json.loads(item[k])
                    else:
                        item[k] = None
            items.append(item)
    return items


def items_to_ndjsongz(items, file_path):
    with gzip.open(file_path, 'wb') as f:
        for item in items:
            line = json.dumps(item, ensure_ascii=False) + '\n'
            f.write(line.encode('utf-8'))


def ndjsongz_to_items(file_path):
    with gzip.open(file_path, 'rb') as f:
        for line in f:
            if line:
                yield json.loads(line)


def items_to_es(items, es_index, es_pk):
    index_or_update_rows(items, index=es_index, pk=es_pk)


def pgcsv_to_es(csv_path, es_index, es_pk, json_fields):
    items = pgcsv_to_items(csv_path, json_fields)
    items_to_es(items, es_index, es_pk)


def ndjsongz_to_es(file_path, es_index, es_pk):
    items = ndjsongz_to_items(file_path)
    items_to_es(items, es_index, es_pk)
