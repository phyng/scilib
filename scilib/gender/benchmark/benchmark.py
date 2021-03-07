# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function, division

import os
import re
import pandas as pd
from scilib.gender.imdb_wiki_dataset.public import load_test_data
from scilib.gender.gender_predictor.public import batch_classify as batch_classify1

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

    metrics['accuracy'] = (metrics['male-male'] + metrics['female-female']) / metrics['total_count']
    return metrics


def run():
    test_data = load_test_data()
    names = [item['name'] for item in test_data]
    configs = [
        ['gender_predictor', batch_classify1],
    ]
    benchmark_results = []
    for name, method in configs:
        print(f'\n\nbenckmark: {name} start')
        results = method(names)
        metrics = _get_result_summary(test_data, results)
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
