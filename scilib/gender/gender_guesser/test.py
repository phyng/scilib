# coding: utf-8

import gender_guesser.detector as gender


def test():
    d = gender.Detector(case_sensitive=False)
    print(d.get_gender(u"Bob"))


if __name__ == '__main__':
    test()
