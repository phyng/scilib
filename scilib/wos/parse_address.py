# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function, division


def parse_address(text):
    """ parse WOS C1 field
    """
    if not text or str(text) == 'nan':
        return []
    state = 'NAME'  # NAME | ADDRESS | ADDRESS_END
    name = ''
    address = ''

    results = []
    for c in text:
        if state == 'NAME':
            if c == ']':
                state = 'ADDRESS'
                continue
            elif c == '[':
                continue
            else:
                name += c
                continue
        elif state == 'ADDRESS':
            if c == '[':
                results.append((name, address))
                state = 'NAME'
                name = ''
                address = ''
                continue
            elif c == ' ' and address == '':
                continue
            else:
                address += c
                continue
        else:
            raise ValueError(state)

    if name and address:
        results.append((name, address))
    return results
