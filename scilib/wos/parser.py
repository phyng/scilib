# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function, division

from .parse_common import parse_is_article, parse_is_oa, parse_py_datetime
from .parse_categorys import parse_ecoom_categorys
from .parse_country import parse_country
from .parse_doi import parse_cr_dois
from .parse_tags import parse_tags

from .parse_orcid import parse_orcid_info
from .parse_address import parse_address_info
from .parse_rid import parse_rid_info


def convert_field_type(item):
    array_keys = [
        'ecoom_categorys',
        'countrys_c1',
        'countrys_rp',
        'countrys_c1_rp',
        'cr_dois',
        'tags',
    ]
    for key in array_keys:
        item[key] = item[key].split(';') if item[key] else []
    for key in item.keys():
        if str(item[key]) == 'nan':
            item[key] = None


def parse_version1(items):
    """ version1

    - parser_version
    - is_article
    - is_oa
    - py_datetime
    - ecoom_categorys
    - countrys_c1
    - countrys_rp
    - countrys_c1_rp
    - cr_dois
    - tags
    """

    for row in items:
        row['parser_version'] = 1
        row['is_article'] = parse_is_article(row)
        row['is_oa'] = parse_is_oa(row)
        row['py_datetime'] = parse_py_datetime(row)

        row['ecoom_categorys'] = parse_ecoom_categorys(row)
        row['countrys_c1'] = parse_country(row, field='C1', hmt=True)
        row['countrys_rp'] = parse_country(row, field='RP', hmt=True)
        row['countrys_c1_rp'] = parse_country(row, field='C1', extra_field='RP', hmt=True)
        row['cr_dois'] = parse_cr_dois(row)
        row['tags'] = parse_tags(row)

        row['c1_address_info'] = parse_address_info(row.get('C1', ''))
        row['orcid_info'] = parse_orcid_info(row.get('OI', ''))
        row['rid_info'] = parse_rid_info(row.get('RI', ''))

        convert_field_type(row)
