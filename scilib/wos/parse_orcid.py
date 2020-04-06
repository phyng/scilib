# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function, division


def parse_orcid(text):
    """ parse OI field
    """
    if not text or str(text) == 'nan':
        return []
    state = 'NAME'  # NAME | ORCID
    name = ''
    orcid = ''

    results = []
    for c in text:
        if state == 'NAME':
            if c == '/':
                state = 'ORCID'
                continue
            elif name == '' and c in [' ', ';']:
                continue
            else:
                name += c
        elif state == 'ORCID':
            if len(orcid) == 19:
                results.append((name, orcid))
                state = 'NAME'
                name = ''
                orcid = ''
                continue
            elif c in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '-', 'X']:
                orcid += c
            else:
                state = 'NAME'
                name += c
                continue
        else:
            raise ValueError(state)

    if name and orcid:
        results.append((name, orcid))
    return results
