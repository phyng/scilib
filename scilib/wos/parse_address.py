# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function, division

from .parse_country import parse_country

ORG_MAP = {
    "Beijing Univ": "Peking Univ",
    "Tsing Hua Univ": "Tsinghua Univ",
    "Xian Jiaotong Univ": "Xi An Jiao Tong Univ",
    "Renmin Univ": "Renmin Univ China",
    "East China Normal Univ": "E China Normal Univ",
    "SW Univ Finance & Econ": "Southwestern Univ Finance & Econ",
    "South China Univ Technol": "S China Univ Technol",
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


def parse_rp_address(text):
    """ parse name and address from WOS RP field

    eg:
    Kurniawan, TA (corresponding author), Xiamen Univ, Coll Ecol & Environm, Xiamen 361102, Peoples R China.;
    """
    if not text or str(text) == 'nan':
        return []

    state = 'NAME'  # NAME | CORRESPONDING | ADDRESS
    name = ''
    address = ''

    results = []
    for c in text:
        if state == 'NAME':
            if c == '(':
                state = 'CORRESPONDING'
                continue
            else:
                name += c
                continue
        elif state == 'CORRESPONDING':
            if c == ',':
                state = 'ADDRESS'
                name = name.strip()
                continue
            else:
                continue
        elif state == 'ADDRESS':
            if c == ';':
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


def parse_rp_address_info(text, *, hmt=True):
    results = parse_rp_address(text)
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
