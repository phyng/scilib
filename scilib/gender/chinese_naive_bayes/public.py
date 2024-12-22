# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function, division

from .chinese_gender import ChineseGenderPredictor, load_featureset


def batch_classify(names, *, tran_group='github'):
    predictor = ChineseGenderPredictor()
    tran_featureset = load_featureset(f'names_{tran_group}.csv')
    predictor.train(tran_featureset)

    results = []
    for name in names:
        if not name:
            results.append('unknown')
            continue
        result = predictor.predict(name, None)
        if result in ['M']:
            results.append('male')
        elif result in ['F']:
            results.append('female')
        else:
            results.append('unknown')
    return results


def test():
    results = batch_classify(["李彩霞", "王大雷", "江铜"])
    print(results)


if __name__ == '__main__':
    test()
