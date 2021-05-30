# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function, division

import os
import re
import pandas as pd
from scilib.gender.imdb_wiki_dataset.public import load_test_data
from scilib.gender.gender_predictor.public import batch_classify as batch_classify1
from scilib.gender.gender_guesser_pypi.public import batch_classify as batch_classify2
from scilib.gender.genderizer_pypi.public import batch_classify as batch_classify3
from scilib.gender.agefromname_pypi.public import batch_classify as batch_classify4
from scilib.gender.gender_r.public import batch_classify as batch_classify5
from scilib.gender.go_gender.public import batch_classify as batch_classify6
from scilib.gender.gender_detector.public import batch_classify as batch_classify7

from scilib.gender.api_genderize.public import batch_classify as batch_classify11
from scilib.gender.api_namsor.public import batch_classify as batch_classify12
from scilib.gender.api_gender.public import batch_classify as batch_classify13

BASE_DIR = os.path.dirname(__file__)
CSV_PATH = os.path.join(BASE_DIR, 'results.csv')
MD_PATH = os.path.join(BASE_DIR, 'README.md')


def _get_result_summary(test_data, results):
    metrics = {
        'total_count': len(results),
        'male-male': 0,
        'male-female': 0,
        'male-unknown': 0,
        'female-male': 0,
        'female-female': 0,
        'female-unknown': 0,
    }
    for index, item in enumerate(test_data):
        key = item['gender'] + '-' + results[index]
        if key not in metrics:
            raise ValueError(key)
        metrics[key] += 1

    m = metrics
    m['accuracy1'] = (m['male-male'] + m['female-female']) / m['total_count']
    m['accuracy2'] = (m['male-male'] + m['female-female']) / (m['male-female'] + m['female-male'] + m['male-male'] + m['female-female'])  # noqa
    m['score1'] = (m['male-female'] + m['male-unknown'] + m['female-male'] + m['female-unknown']) / m['total_count']
    m['score2'] = (m['male-female'] + m['female-male']) / (m['male-female'] + m['female-male'] + m['male-male'] + m['female-female'])  # noqa
    m['score3'] = (m['male-unknown'] + m['female-unknown']) / m['total_count']
    m['score4'] = (m['male-female'] - m['female-male']) / (m['male-female'] + m['female-male'] + m['male-male'] + m['female-female']) # noqa
    return m


def run():
    test_data = load_test_data()
    names = [item['name'] for item in test_data]
    configs = [
        ['gender-api.com', batch_classify13, dict(limit=500)],
        ['genderize.io', batch_classify11, dict(limit=1000)],
        ['namsor.com', batch_classify12, dict(limit=2000)],

        ['gender_predictor', batch_classify1, {}],
        ['gender_guesser', batch_classify2, {}],
        ['genderizer', batch_classify3, {}],
        ['gender@R', batch_classify5, {}],
        ['agefromname', batch_classify4, {}],
        ['gender@go', batch_classify6, {}],
        ['gender_detector', batch_classify7, {}],
    ]
    benchmark_results = []
    for name, method, options in configs:
        print(f'\n\nbenckmark: {name} start')
        limit = options.get('limit') or len(test_data)
        results = method(names[:limit])
        metrics = _get_result_summary(test_data[:limit], results)
        print(metrics)
        benchmark_results.append(dict(name=name, **metrics))
    df = pd.DataFrame.from_records(benchmark_results)
    df.to_csv(CSV_PATH, index=False)

    markdown_content = df.to_markdown(index=False)
    with open(MD_PATH, 'r+') as f:
        content = f.read()
        new_content = re.sub(r'(?sm)(BENCHMARK_START -->).*(<!-- BENCHMARK_END)', rf'\1\n{markdown_content}\n\2', content)  # noqa
        f.seek(0)
        f.write(new_content)


if __name__ == '__main__':
    run()
