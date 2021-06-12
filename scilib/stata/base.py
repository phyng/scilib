# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function, division

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def call(*args):
    return ' '.join(args)


def call_batch(*line):
    return '\n'.join(line)


def call_quietly(code):
    return call_batch(
        call('qui{'),
        code,
        call('}'),
    )


def call_from_file(do_file, **kwargs):
    with open(os.path.join(BASE_DIR, do_file)) as f:
        content = f.read()
    for k, v in kwargs.items():
        content = content.replace(k, v)
    return content
