# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function, division

from .genderPredictor import genderPredictor


def batch_classify(names):
    gp = genderPredictor()
    gp.trainAndTest()

    first_names = [i.split()[0] if i and i.split() else '' for i in names]
    results = []
    for first_name in first_names:
        if not first_name:
            results.append('error')
            continue
        result = gp.classify(first_name)
        if result == 'M':
            results.append('male')
        elif result == 'F':
            results.append('female')
        else:
            results.append('unknown')
    return results
