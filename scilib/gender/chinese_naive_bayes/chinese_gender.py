# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function, division

import os
import random
from functools import lru_cache
import pandas as pd
from nltk import NaiveBayesClassifier, classify

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, 'data')


@lru_cache(maxsize=None)
def get_double_names():
    df_double = pd.read_excel(os.path.join(DATA_DIR, 'double_names.xlsx'))
    double_names = set([row['name'] for i, row in df_double.iterrows()])
    return double_names


def get_name_features(name):
    double_names = get_double_names()
    if '·' in name:
        return
    name = ''.join([i for i in name if i])
    if len(name) not in [2, 3, 4]:
        return
    if name[:2] in double_names or len(name) == 4:
        # first_name = name[:2]
        last_name = name[2:]
    else:
        # first_name = name[:1]
        last_name = name[1:]
    features = {
        'last_name': last_name,
        'last_name_0': None,
        'last_name_1': None,
        'last_name_repeat': len(last_name) == 2 and last_name[0] == last_name[1]
    }

    for index, token in enumerate(last_name):
        features[f'last_name_{index}'] = token
    return features


def load_featureset(names_file):
    df_names = pd.read_csv(os.path.join(DATA_DIR, names_file))
    df_names = df_names.drop_duplicates(['name'])
    print(f'{names_file} count={df_names.shape}')

    featureset = []
    for i, row in df_names.iterrows():
        name = str(row['name']).strip()
        gender = str(row['gender']).strip()
        if gender not in ['男', '女']:
            continue
        gender = 'M' if gender == '男' else 'F'
        features = get_name_features(name)
        if not features:
            continue
        featureset.append((features, gender))

    print(f'{names_file} featureset={len(featureset)}')
    random.shuffle(featureset)
    featureset_m = [i for i in featureset if i[1] == 'M']
    featureset_f = [i for i in featureset if i[1] == 'F']
    print(f'{names_file} M={len(featureset_m)} F={len(featureset_f)}')
    min_size = min(len(featureset_m), len(featureset_f))
    return (featureset_m[:min_size] + featureset_f[:min_size])


class ChineseGenderPredictor(object):

    def __init__(self):
        self.training_percent = 0.8
        self.classifier = None

    def train_and_test(self, featureset=None, train_set=None, test_set=None):
        if not (train_set and test_set):
            random.shuffle(featureset)
            break_point = int(len(featureset) * self.training_percent)
            train_set = train_set or featureset[:break_point]
            test_set = test_set or featureset[break_point:]

        self.classifier = NaiveBayesClassifier.train(train_set)
        accuracy = classify.accuracy(self.classifier, test_set)
        return accuracy

    def get_most_informative_features(self, n=5):
        return self.classifier.most_informative_features(n)

    def predict(self, name):
        features = get_name_features(name)
        if not features:
            return None, None
        return self.classifier.prob_classify(features).prob('M'), self.classifier.prob_classify(features).prob('F')


def test_file(names_file):
    featureset = load_featureset(names_file)
    predictor = ChineseGenderPredictor()
    accuracy = predictor.train_and_test(featureset)
    return accuracy


def cross_test():
    github_featureset = load_featureset('names_github.csv')
    web_featureset = load_featureset('names_web.csv')
    nsfc_featureset = load_featureset('names_nsfc.csv')
    zero_featureset = load_featureset('names_zero.csv')

    for group, tran, test in [
        ('github_web', github_featureset, web_featureset),
        ('github_nsfc', github_featureset, nsfc_featureset),
        ('github_zero', github_featureset, zero_featureset),
        ('web_nsfc', web_featureset, nsfc_featureset),
        ('web_github', web_featureset, github_featureset),
        ('web_zero', web_featureset, zero_featureset),
        ('zero_nsfc', zero_featureset, nsfc_featureset),
        ('zero_github', zero_featureset, github_featureset),
        ('zero_web', zero_featureset, web_featureset),
    ]:
        predictor = ChineseGenderPredictor()
        accuracy = predictor.train_and_test(train_set=tran, test_set=test)
        print(f'group={group} accuracy={accuracy}')


if __name__ == '__main__':
    cross_test()

    for names_file in ['names_web.csv', 'names_github.csv']:
        print(f'use_file={names_file}')
        print('accuracy', test_file(names_file))
