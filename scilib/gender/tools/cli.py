# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function, division

import re
import pandas as pd
from optparse import OptionParser

from scilib.gender.gender_guesser_pypi.public import batch_classify


def run(from_excel, to_excel):
    df = pd.read_excel(from_excel, engine='openpyxl')
    items = []
    for index, row in df.iterrows():
        names = re.split(r'[ ,|]', str(row['Authors']))
        if not names:
            items.append(row)
            continue
        name = names[0]
        items.append({
            **row,
            'gender_guesser_name': name,
            'gender_guesser': batch_classify([name + ' '])[0]
        })
    pd.DataFrame.from_records(items).to_excel(to_excel)


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("--from-excel", action="store", type="str", dest="from_excel", default=None)
    parser.add_option("--to-excel", action="store", type="str", dest="to_excel", default=None)
    options, args = parser.parse_args()
    run(options.from_excel, options.to_excel)
