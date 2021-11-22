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


@lru_cache(maxsize=None)
def load_names_file(names_file):
    df_names = pd.read_csv(os.path.join(DATA_DIR, names_file))
    df_names = df_names.drop_duplicates(['name'])
    # print(f'  {names_file} count={df_names.shape}')

    items = []
    for i, row in df_names.iterrows():
        name = str(row['name']).strip()
        gender = str(row['gender']).strip()
        if gender not in ['男', '女']:
            continue
        gender = 'M' if gender == '男' else 'F'
        if len(name) not in [2, 3, 4]:
            continue
        items.append(dict(name=name, gender=gender))
    return items


def load_featureset(names_file):
    items = load_names_file(names_file)
    featureset = []
    for item in items:
        name = item['name']
        gender = item['gender']
        features = get_name_features(name)
        if not features:
            continue
        featureset.append((features, gender))

    random.shuffle(featureset)
    print(f'  {names_file} featureset={len(featureset)}')
    # featureset_m = [i for i in featureset if i[1] == 'M']
    # featureset_f = [i for i in featureset if i[1] == 'F']
    # print(f'{names_file} M={len(featureset_m)} F={len(featureset_f)}')
    return featureset


class ChineseGenderPredictor(object):

    def __init__(self):
        self.training_percent = 0.8
        self.classifier = None

    def train(self, featureset):
        self.classifier = NaiveBayesClassifier.train(featureset)

    def train_and_test(self, featureset=None, train_set=None, test_set=None):
        if not (train_set and test_set):
            random.shuffle(featureset)
            break_point = int(len(featureset) * self.training_percent)
            train_set = train_set or featureset[:break_point]
            test_set = test_set or featureset[break_point:]

        self.train(train_set)
        accuracy = classify.accuracy(self.classifier, test_set)
        return accuracy

    def get_most_informative_features(self, n=5):
        return self.classifier.most_informative_features(n)

    def predict(self, name, last_name_length=None):
        features = get_name_features(name)
        if not features:
            return None
        if last_name_length is not None and len(features['last_name']) != last_name_length:
            return None
        prob = self.classifier.prob_classify(features)
        prob_m = prob.prob('M')
        prob_f = prob.prob('F')
        if prob_m > prob_f:
            return 'M'
        elif prob_m < prob_f:
            return 'F'
        else:
            return 'O'

    def test(self, items, name_map=None, last_name_length=None):
        right_count = 0
        error_count = 0
        for item in items:
            if name_map and item['name'] in name_map:
                predict_value = name_map[item['name']]
            else:
                predict_value = self.predict(item['name'], last_name_length=last_name_length)
            if predict_value is None:
                continue
            if predict_value == item['gender']:
                right_count += 1
            else:
                error_count += 1
        if (right_count + error_count) == 0:
            return 0
        return right_count / (right_count + error_count)


def test_file(names_file):
    featureset = load_featureset(names_file)
    predictor = ChineseGenderPredictor()
    accuracy = predictor.train_and_test(featureset)
    return accuracy


def test_group():
    for tran_group, test_group in [
        ('github', 'github'),
        ('github', 'nsfc'),
        ('github', 'zero'),
        ('github', 'web'),

        ('web', 'web'),
        ('web', 'nsfc'),
        ('web', 'github'),
        ('web', 'zero'),
    ]:
        tran_items = load_names_file(f'names_{tran_group}.csv')
        tran_featureset = load_featureset(f'names_{tran_group}.csv')
        test_items = load_names_file(f'names_{test_group}.csv')
        test_featureset = load_featureset(f'names_{test_group}.csv')

        if tran_group == test_group:
            predictor = ChineseGenderPredictor()
            accuracy_self = predictor.train_and_test(featureset=tran_featureset)
            print(f'{tran_group}-{tran_group} accuracy_self={accuracy_self}')
        else:
            predictor = ChineseGenderPredictor()
            accuracy = predictor.train_and_test(train_set=tran_featureset, test_set=test_featureset)
            print(f'{tran_group}-{test_group} accuracy={accuracy}')

            accuracy_with_map = predictor.test(test_items, {i['name']: i['gender'] for i in tran_items})
            print(f'{tran_group}-{test_group} accuracy_with_map={accuracy_with_map}')

            accuracy_with_last_name_length1 = predictor.test(test_items, last_name_length=1)
            print(f'{tran_group}-{test_group} accuracy_with_last_name_length1={accuracy_with_last_name_length1}')

            accuracy_with_last_name_length2 = predictor.test(test_items, last_name_length=2)
            print(f'{tran_group}-{test_group} accuracy_with_last_name_length2={accuracy_with_last_name_length2}')


if __name__ == '__main__':
    test_group()
