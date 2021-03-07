# coding: utf-8

import gender_guesser.detector as gender


def batch_classify(names):
    first_names = [i.split()[0] for i in names]
    results = []
    d = gender.Detector(case_sensitive=False)
    for first_name in first_names:
        result = d.get_gender(first_name)
        if result in ['male', 'mostly_male']:
            results.append('male')
        elif result in ['female', 'mostly_female']:
            results.append('female')
        else:
            results.append('unknown')
    return results


def test():
    d = gender.Detector(case_sensitive=False)
    print(d.get_gender(u"Bob"))


if __name__ == '__main__':
    test()
