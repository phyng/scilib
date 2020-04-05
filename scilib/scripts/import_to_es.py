# coding: utf-8

""" import WOS data to ElasticSearch
"""

from __future__ import unicode_literals, absolute_import, print_function, division

import asyncio
from optparse import OptionParser

from wos.importer import read_text_format_dir_parallel, read_text_format_path
from wos.parser import parse_version1
from db.es import index_or_update_rows


def callback(path):
    items = read_text_format_path(path)
    parse_version1(items)
    index_or_update_rows(items, index='wos2', action='index')


async def main(from_dir):
    await read_text_format_dir_parallel(from_dir, callback)


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("--from", action="store", type="str", dest="from_dir", default=".")
    options, args = parser.parse_args()
    asyncio.run(main(options.from_dir))
