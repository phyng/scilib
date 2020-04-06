# coding: utf-8

""" import WOS data to ElasticSearch
"""

from __future__ import unicode_literals, absolute_import, print_function, division

import asyncio
from optparse import OptionParser

from scilib.wos.importer import read_text_format_dir_parallel, read_text_format_path
from scilib.wos.parser import parse_version1
from scilib.db.es import index_or_update_rows


def callback(path, index):
    items = read_text_format_path(path)
    parse_version1(items)
    index_or_update_rows(items, index=index, action='index')


async def main(from_dir, index):
    await read_text_format_dir_parallel(from_dir, callback, index)


def run():
    parser = OptionParser()
    parser.add_option("--from", action="store", type="str", dest="from_dir", default=".")
    parser.add_option("--to", action="store", type="str", dest="to", default="es")
    parser.add_option("--index", action="store", type="str", dest="index", default="wos")
    options, args = parser.parse_args()
    asyncio.run(main(options.from_dir, options.index))


if __name__ == '__main__':
    run()
