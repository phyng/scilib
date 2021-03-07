# coding: utf-8

import os
import subprocess
from scilib.iterlib import chunks

BASE_DIR = os.path.dirname(__file__)
R_PATH = os.path.join(BASE_DIR, 'gender.R')


def batch_classify(names):
    first_names = [i.split()[0] for i in names]

    output_results = {}
    for chunk in chunks(first_names, size=500):
        output = subprocess.check_output([
            'Rscript',
            R_PATH,
            '--name',
            ','.join(chunk),
        ]).decode('utf-8')
        output_results.update(dict([i.strip().split(',') for i in output.split('\n') if i.strip()]))

    results = []
    for first_name in first_names:
        result = output_results.get(first_name, "unknown")
        if result in ['male']:
            results.append('male')
        elif result in ['female']:
            results.append('female')
        else:
            results.append('unknown')
    return results


def test():
    results = batch_classify(["tom", "lisa", "bob", "test10086"])
    print(results)


if __name__ == '__main__':
    test()
