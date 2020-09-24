# coding: utf-8

""" import cnki data
"""

from __future__ import unicode_literals, absolute_import, print_function, division

import asyncio
import pandas as pd
from optparse import OptionParser

from scilib.cnki.importer import read_text_format_dir, collect_keywords


async def main(from_dir, to_type):
    items = read_text_format_dir(from_dir)
    df = pd.DataFrame.from_records(items)
    df = df.drop_duplicates(subset=['Title'])
    print('df.shape', df.shape)
    df.to_excel(to_type)

    counter, counter_map, years_items_flat, corrs = collect_keywords([dict(i) for index, i in df.iterrows()])
    counter_items = [dict(k=k, v=v) for k, v in counter.most_common()]
    pd.DataFrame.from_records(counter_items).to_excel(to_type + '.counter.xlsx')
    pd.DataFrame.from_records(years_items_flat).to_excel(to_type + '.years_items_flat.xlsx')
    pd.DataFrame.from_records(corrs).to_excel(to_type + '.corrs.xlsx')
    pd.DataFrame.from_records(corrs).to_csv(to_type + '.corrs.csv')


def run():
    parser = OptionParser()
    parser.add_option("--from", action="store", type="str", dest="from_dir", default=".")
    parser.add_option("--to", action="store", type="str", dest="to", default="count")

    options, args = parser.parse_args()
    asyncio.run(main(options.from_dir, options.to))


if __name__ == '__main__':
    run()
