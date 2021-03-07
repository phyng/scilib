# coding: utf-8

from genderizer.genderizer import Genderizer


def batch_classify(names):
    first_names = [i.split()[0].lower() for i in names]
    results = []
    for first_name in first_names:
        result = Genderizer.detect(firstName=first_name)
        if result in ['male']:
            results.append('male')
        elif result in ['female']:
            results.append('female')
        else:
            results.append('unknown')
    return results
