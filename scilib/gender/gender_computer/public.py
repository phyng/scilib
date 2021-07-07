# coding: utf-8

from .genderComputer.genderComputer import GenderComputer


def batch_classify(names):
    gc = GenderComputer()

    results = []
    for name in names:
        result = gc.resolveGender(name, None)
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
