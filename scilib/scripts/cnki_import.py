# coding: utf-8

""" import cnki data
"""

from __future__ import unicode_literals, absolute_import, print_function, division

import asyncio
import pandas as pd
from optparse import OptionParser
from scilib.cnki.importer import read_text_format_dir, read_spider_format_dir
from scilib.cnki.keywords import collect_keywords
from scilib.cnki.importer import read_spider_format, read_spider_format_dir_parallel
from scilib.db.es import index_or_update_rows


def es_callback(path):
    try:
        items = list(read_spider_format(path))
        print(len(items))
        index_or_update_rows(items, index='cnki_nsfc', action='index', pk='list_id')
    except Exception as e:
        print(e)
        return


async def main(from_dir, to, from_type, to_type, fields):
    fields = fields.split(',') if fields else []
    df = None

    if from_type == 'text':
        items = read_text_format_dir(from_dir)
        df = pd.DataFrame.from_records(items)
        # df = df.drop_duplicates(subset=['Title'])
    elif from_type == 'spider':
        items = read_spider_format_dir(from_dir, fields=fields)
        df = pd.DataFrame.from_records(items)
        # df = df.drop_duplicates(subset=['Title'])
    elif from_type == 'spider_parallel':
        if to_type == 'parallel_es':
            await read_spider_format_dir_parallel(from_dir, callback=es_callback)
    else:
        raise ValueError(f'unknown from type: {from_type}')

    if to_type == 'corr':
        print('df.shape', df.shape)
        df.to_excel(to)
        result = collect_keywords([dict(i) for index, i in df.iterrows()])
        counter_items = [dict(k=k, v=v) for k, v in result['counter'].most_common()]
        pd.DataFrame.from_records(counter_items).to_excel(to + '.counter.xlsx')
    elif to_type == 'excel':
        if fields:
            df = df[fields]
        df.to_excel(to)
    elif to_type == 'csv':
        if fields:
            df = df[fields]
        df.to_csv(to)
    elif to_type == 'parallel_es':
        pass
    else:
        raise ValueError(f'unknown to type: {to_type}')


def run():
    parser = OptionParser()
    parser.add_option("--from", action="store", type="str", dest="from_dir", default=".")
    parser.add_option("--to", action="store", type="str", dest="to", default="count")
    parser.add_option("--from-type", action="store", type="str", dest="from_type", default="text")
    parser.add_option("--to-type", action="store", type="str", dest="to_type", default="corr")
    parser.add_option("--fields", action="store", type="str", dest="fields", default="")

    options, args = parser.parse_args()
    asyncio.run(main(options.from_dir, options.to, options.from_type, options.to_type, options.fields))


if __name__ == '__main__':
    run()
