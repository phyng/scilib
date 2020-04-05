# coding: utf-8

""" import WOS data to ElasticSearch
"""

from __future__ import unicode_literals, absolute_import, print_function, division

import asyncio
from optparse import OptionParser
from wos.importer import read_text_format_dir_parallel, read_text_format_path


def worker(path):
    items = read_text_format_path(path)
    return [item['UT'] for item in items]


async def count_uts(from_dir):
    results = await read_text_format_dir_parallel(from_dir, worker)
    uts = set()
    for result in results:
        uts.update(result)
    print(len(uts))


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option(
        "--from",
        action="store",
        type="str",
        dest="from_dir",
        default=".",
    )
    options, args = parser.parse_args()
    asyncio.run(count_uts(options.from_dir))
