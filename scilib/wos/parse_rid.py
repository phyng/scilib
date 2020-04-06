# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function, division

import re


def parse_rid(text):
    """ parse RI field
    """
    if not text or str(text) == 'nan':
        return []
    state = 'NAME'  # NAME | RID
    name = ''
    rid = ''

    results = []
    for c in text:
        if state == 'NAME':
            if c == '/':
                state = 'RID'
                continue
            elif name == '' and c in [' ', ';']:
                continue
            else:
                name += c
        elif state == 'RID':
            if rid.count('-') == 2 and re.search(r'-\d{4}$', rid):
                results.append((name, rid))
                state = 'NAME'
                name = ''
                rid = ''
                continue
            else:
                rid += c
                continue
        else:
            raise ValueError(state)

    if name and rid:
        results.append((name, rid))
    return results


def parse_rid_info(text):
    results = parse_rid(text)
    infos = []
    for name, rid in results:
        infos.append(dict(
            name=name,
            rid=rid,
        ))
    return infos
