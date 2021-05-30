# coding: utf-8

import os
import json
import requests
from .secret import X_API_KEY

BASE_DIR = os.path.dirname(__file__)
DATA_PATH = os.path.join(BASE_DIR, 'data')


def batch_classify(names):
    names = [i.replace('/', '') for i in names]

    output_results = {}
    for name in names:
        file_path = os.path.join(DATA_PATH, f'{name}.json')
        if os.path.exists(file_path):
            with open(file_path) as f:
                data = json.load(f)
                output_results[name] = data['likelyGender']
                continue
        response = requests.get(f'https://v2.namsor.com/NamSorAPIv2/api2/json/genderFull/{name}', headers={
            'X-API-KEY': X_API_KEY
        })
        response.raise_for_status()
        data = response.json()
        print('data', data)
        if 'likelyGender' in data:
            output_results[name] = data['likelyGender']
            with open(file_path, 'w') as f:
                json.dump(data, f)
        else:
            raise ValueError([name, data])

    results = []
    for name in names:
        result = output_results.get(name, "unknown")
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
