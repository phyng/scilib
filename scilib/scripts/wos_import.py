# coding: utf-8

""" import WOS data
"""

from __future__ import unicode_literals, absolute_import, print_function, division

import asyncio
import pandas as pd
from optparse import OptionParser

from scilib.wos.importer import read_text_format_dir_parallel, read_text_format_path
from scilib.wos.parser import parse_version1
from scilib.db.es import index_or_update_rows


def es_callback(path, index):
    items = read_text_format_path(path)
    parse_version1(items)
    index_or_update_rows(items, index=index, action='index')


def csv_callback(path, fields, tag, py_from, py_to):
    fields = fields.split(',')

    items = read_text_format_path(path)
    parse_version1(items)
    if tag:
        tags = set([i.strip() for i in tag.split(',') if i.strip()])
        items = [item for item in items if set(item['tags']).issuperset(tags)]
    if py_from and py_to:
        pys = [str(i) for i in range(int(py_from), int(py_to) + 1)]
        items = [item for item in items if item.get('PY', '') in pys]

    return [{k: v for k, v in item.items() if k in fields} for item in items]


def count_callback(path):
    items = read_text_format_path(path)
    return len(items)


def cr_query_callback(path, tag):
    items = read_text_format_path(path)
    parse_version1(items)
    download_dois = set([item['DI'] for item in items if str(item.get('DI', '')).startswith('10.')])
    if tag:
        tags = set([i.strip() for i in tag.split(',') if i.strip()])
        items = [item for item in items if set(item['tags']).issuperset(tags)]
    cr_dois = set()
    for item in items:
        cr_dois.update(item['cr_dois'])
    return download_dois, cr_dois


async def main(from_dir, to_type, index, fields, tag, py_from, py_to):
    if to_type == 'es':
        await read_text_format_dir_parallel(from_dir, es_callback, index)
    elif to_type == 'count':
        results = await read_text_format_dir_parallel(from_dir, count_callback)
        print(sum(results))
    elif to_type == 'cr_query':
        results = await read_text_format_dir_parallel(from_dir, cr_query_callback, tag)
        download_dois = set.union(*[set(li[0]) for li in results])
        cr_dois = set.union(*[set(li[1]) for li in results])
        new_dois = cr_dois - download_dois
        print(f'download_dois={len(download_dois)} cr_dois={len(cr_dois)} new_dois={len(new_dois)}')
    elif to_type.endswith('.csv'):
        results = await read_text_format_dir_parallel(from_dir, csv_callback, fields, tag, py_from, py_to)
        df = pd.DataFrame.from_records((i for li in results for i in li))
        print(df.shape)
        df.to_csv(to_type)
    elif to_type.endswith('.xlsx'):
        results = await read_text_format_dir_parallel(from_dir, csv_callback, fields, tag, py_from, py_to)
        df = pd.DataFrame.from_records((i for li in results for i in li))
        print(df.shape)
        df.to_excel(to_type)
    else:
        raise ValueError(to_type)


def run():
    parser = OptionParser()
    parser.add_option("--from", action="store", type="str", dest="from_dir", default=".")
    parser.add_option("--to", action="store", type="str", dest="to", default="count")
    parser.add_option("--index", action="store", type="str", dest="index", default="wos")
    parser.add_option("--fields", action="store", type="str", dest="fields", default="UT")

    parser.add_option("--tag", action="store", type="str", dest="tag", default=None)
    parser.add_option("--py_from", action="store", type="str", dest="py_from", default=None)
    parser.add_option("--py_to", action="store", type="str", dest="py_to", default=None)

    options, args = parser.parse_args()
    asyncio.run(main(
        options.from_dir, options.to, options.index, options.fields, options.tag, options.py_from, options.py_to
    ))


if __name__ == '__main__':
    run()
