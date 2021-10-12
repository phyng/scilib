# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function, division
import os
import pandas as pd

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, 'data')


def load_from_github(path):
    """ https://github.com/wainshine/Chinese-Names-Corpus/tree/master/Chinese_Names_Corpus
    """
    items = []
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.endswith(',男') or line.endswith(',女') or line.endswith(',未知'):
                [name, gender] = line.split(',')
                items.append(dict(
                    name=name,
                    gender=gender,
                ))
                if len(items) % 10000 == 0:
                    print(len(items))

    print(f'total_count={len(items)}')
    df = pd.DataFrame.from_records(items)
    df.to_csv(os.path.join(DATA_DIR, 'names_github.csv'))


if __name__ == '__main__':
    load_from_github()
