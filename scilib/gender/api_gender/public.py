# coding: utf-8

import os
import json
import requests
from .secret import X_API_KEY

BASE_DIR = os.path.dirname(__file__)
DATA_PATH = os.path.join(BASE_DIR, 'data')


def batch_classify(names):
    first_names = [i.split()[0].replace('/', '') for i in names]

    output_results = {}
    for first_name in first_names:
        file_path = os.path.join(DATA_PATH, f'{first_name}.json')
        if os.path.exists(file_path):
            with open(file_path) as f:
                data = json.load(f)
                output_results[first_name] = data['gender']
                continue
        response = requests.get('https://gender-api.com/get', {'name': first_name, 'key': X_API_KEY})
        response.raise_for_status()
        data = response.json()
        print('data', data)
        if 'gender' in data:
            output_results[first_name] = data['gender']
            with open(file_path, 'w') as f:
                json.dump(data, f)
        else:
            raise ValueError([first_name, data])

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
