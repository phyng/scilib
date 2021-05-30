# coding: utf-8

import os
import subprocess
from scilib.iterlib import chunks

BASE_DIR = os.path.dirname(__file__)
CLI_PATH = os.path.join(BASE_DIR, 'cli.rb')


def batch_classify(names):
    first_names = [i.split()[0].replace(',', '') for i in names]

    output_results = {}
    for chunk in chunks(first_names, size=500):
        output = subprocess.check_output([
            'ruby',
            CLI_PATH,
            *chunk
        ], cwd=BASE_DIR).decode('utf-8')
        output_results.update(dict([i.strip().split(',')[:2] for i in output.split('\n') if i.strip()]))

    results = []
    for first_name in first_names:
        result = output_results.get(first_name, "unknown")
        if result in ['male', 'mostly_male']:
            results.append('male')
        elif result in ['female', 'mostly_female']:
            results.append('female')
        else:
            results.append('unknown')
    return results


def test():
    results = batch_classify(["tom", "lisa", "bob", "test10086"])
    print(results)


if __name__ == '__main__':
    test()
