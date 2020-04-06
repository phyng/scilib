# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function, division

from .parse_country import parse_country

ORG_MAP = {
    "Peking Univ": "Peking Univ",
    "Beijing Univ": "Peking Univ",
    "Tsinghua Univ": "Tsinghua Univ",
    "Tsing Hua Univ": "Tsinghua Univ",
    "Xi An Jiao Tong Univ": "Xi An Jiao Tong Univ",
    "Xian Jiaotong Univ": "Xi An Jiao Tong Univ",
    "Renmin Univ China": "Renmin Univ China",
    "Renmin Univ": "Renmin Univ China",
    "E China Normal Univ": "E China Normal Univ",
    "East China Normal Univ": "E China Normal Univ",
    "Southwestern Univ Finance & Econ": "Southwestern Univ Finance & Econ",
    "SW Univ Finance & Econ": "Southwestern Univ Finance & Econ",
    "S China Univ Technol": "S China Univ Technol",
    "South China Univ Technol": "S China Univ Technol",
    "South China Normal Univ": "South China Normal Univ",
    "South China Normal Univ": "South China Normal Univ",
}


def parse_address(text):
    """ parse name and address from WOS C1 field
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


def parse_org(text):
    tokens = [i.strip() for i in text.split(',') if i.strip()]
    if tokens and tokens[0]:
        return ORG_MAP.get(tokens[0], tokens[0])


def parse_address_info(text, *, hmt=True):
    results = parse_address(text)
    infos = []
    for name, address in results:
        org = parse_org(address)
        country = parse_country(dict(C1=address), field='C1', hmt=hmt)
        infos.append(dict(
            name=name,
            address=address,
            org=org,
            country=country,
        ))

    return infos
