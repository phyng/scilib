# coding: utf-8

""" import WOS data to ElasticSearch
"""

from __future__ import unicode_literals, absolute_import, print_function, division

import asyncio
from optparse import OptionParser
from wos.importer import get_uts_parallel


async def count_uts(from_dir):
    print(len(await get_uts_parallel(from_dir)))


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
