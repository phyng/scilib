# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function, division

import os

import random
import pandas as pd
from nltk import NaiveBayesClassifier, classify

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, 'data')


def get_name_features(double_names, name, gender=None):
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


def load_featureset():
    df_names = pd.read_excel(os.path.join(DATA_DIR, 'names.xlsx'))
    df_double = pd.read_excel(os.path.join(DATA_DIR, 'double_names.xlsx'))
    double_names = set([row['name'] for i, row in df_double.iterrows()])
    print(df_names.shape)

    featureset = []
    for i, row in df_names.iterrows():
        name = str(row['name']).strip()
        gender = str(row['gender']).strip()
        if gender not in ['男', '女']:
            continue
        gender = 'M' if gender == '男' else 'F'
        features = get_name_features(double_names, name, gender=gender)
        if not features:
            continue
        featureset.append((features, gender))

    print(f'load featureset count={len(featureset)}')
    random.shuffle(featureset)
    featureset_m = [i for i in featureset if i[1] == 'M']
    featureset_f = [i for i in featureset if i[1] == 'F']
    print(f'M={len(featureset_m)} F={len(featureset_f)}')
    min_size = min(len(featureset_m), len(featureset_f))
    return (featureset_m[:min_size] + featureset_f[:min_size]), double_names


class ChineseGenderPredictor(object):

    def __init__(self, featureset, double_names):
        self.featureset = featureset
        self.double_names = double_names
        self.training_percent = 0.8
        self.classifier = None
        self.tokens_map = None

    def prepare(self, train_set):
        tokens = []
        tokens_map = {}
        for features, gender in train_set:
            if features['last_name_0']:
                tokens.append((features['last_name_0'], gender))
            if features['last_name_1']:
                tokens.append((features['last_name_1'], gender))
        for token, gender in tokens:
            tokens_map.setdefault(token, {'M': 0, 'F': 0})[gender] += 1
        for k, config in tokens_map.items():
            config['m_percent'] = config['M'] / (config['M'] + config['F'])
            config['f_percent'] = config['F'] / (config['M'] + config['F'])
        self.tokens_map = tokens_map

        for features, gender in self.featureset:
            self.set_full_features(features)

    def set_full_features(self, features):
        pass

    def get_name_full_features(self, name):
        features = get_name_features(self.double_names, name)
        self.set_full_features(features)
        return features

    def train_and_test(self):
        random.shuffle(self.featureset)
        count = len(self.featureset)
        break_point = int(count * self.training_percent)
        train_set = self.featureset[:break_point]
        test_set = self.featureset[break_point:]

        self.prepare(train_set)

        self.classifier = NaiveBayesClassifier.train(train_set)
        accuracy = classify.accuracy(self.classifier, test_set)

        return accuracy

    def get_most_informative_features(self, n=5):
        return self.classifier.most_informative_features(n)

    def predict(self, name):
        features = self.get_name_full_features(name)
        if not features:
            return None
        return self.classifier.prob_classify(features).prob('M'), self.classifier.prob_classify(features).prob('F')


def main():
    featureset, double_names = load_featureset()
    predictor = ChineseGenderPredictor(featureset, double_names)
    accuracy = predictor.train_and_test()
    print(accuracy)


if __name__ == '__main__':
    main()
