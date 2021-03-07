# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function, division

import os
import numpy as np
import pandas as pd
from scipy.io import loadmat

BASE_DIR = os.path.dirname(__file__)
WIKI_MAT_PATH = os.path.join(BASE_DIR, 'data/wiki.mat')
WIKI_CSV_PATH = os.path.join(BASE_DIR, 'data/wiki.csv')
WIKI_GENDER_TEST_CSV_PATH = os.path.join(BASE_DIR, 'data/wiki_gender_test.csv')


def mat_data_to_csv():
    mat_data = loadmat(WIKI_MAT_PATH)
    fields = [
        'dob',
        'photo_taken',
        'full_path',
        'gender',
        'name',
        'face_location',
        'face_score',
        'second_face_score',
    ]

    wiki_data = mat_data['wiki']
    array_data = [
        wiki_data[0][0][0][0],
        wiki_data[0][0][1][0],
        [i[0] for i in wiki_data[0][0][2][0]],
        wiki_data[0][0][3][0],
        [i[0] if i.size > 0 else '' for i in wiki_data[0][0][4][0]],
        wiki_data[0][0][5][0],
        wiki_data[0][0][6][0],
        wiki_data[0][0][7][0],
    ]

    np_data = np.vstack(array_data).T
    df = pd.DataFrame(np_data)
    df.columns = fields
    df.to_csv(WIKI_CSV_PATH, index=False)

    # gender test
    items = []
    for index, row in df.iterrows():
        if row['name'] and row['gender'] in [0, 1]:
            items.append(dict(name=row['name'], gender='male' if row['gender'] == 1 else 'female'))
    pd.DataFrame.from_records(items).to_csv(WIKI_GENDER_TEST_CSV_PATH, index=False)


if __name__ == '__main__':
    mat_data_to_csv()
