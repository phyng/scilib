# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function, division

from .parse_common import parse_is_article, parse_is_oa, parse_py_datetime, parse_document_types, parse_fu_tokens
from .parse_categorys import parse_ecoom_categorys
from .parse_country import parse_country, parse_collaboration_type_china, parse_lead_type_china
from .parse_country import parse_collaboration_type, parse_first_country
from .parse_doi import parse_cr_dois
from .parse_tags import parse_tags

from .parse_orcid import parse_orcid_info
from .parse_address import parse_address_info
from .parse_rid import parse_rid_info

ARRAY_KEYS = [
    'document_types',
    'fu_tokens',
    'ecoom_categorys',
    'countrys_c1',
    'countrys_rp',
    'countrys_c1_rp',
    'cr_dois',
    'tags',
]


def add_row_type(item):
    for key in ARRAY_KEYS:
        item[key] = item[key].split(';') if item[key] else []
    for key in item.keys():
        if str(item[key]) == 'nan':
            item[key] = None


def remove_row_type(item):
    for key in ARRAY_KEYS:
        if type(item[key]) is list:
            item[key] = ';'.join([str(i) for i in item[key]])


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
        row['document_types'] = parse_document_types(row)
        row['fu_tokens'] = parse_fu_tokens(row)
        row['is_article'] = parse_is_article(row)
        row['is_oa'] = parse_is_oa(row)
        row['py_datetime'] = parse_py_datetime(row)

        row['countrys_c1'] = parse_country(row, field='C1', hmt=True)
        row['countrys_rp'] = parse_country(row, field='RP', hmt=True)
        row['countrys_c1_rp'] = parse_country(row, field='C1', extra_field='RP', hmt=True)
        row['collaboration_type_china'] = parse_collaboration_type_china(row['countrys_c1_rp'])
        row['lead_type_china'] = parse_lead_type_china(row['countrys_c1_rp'])
        row['collaboration_type'] = parse_collaboration_type(row['countrys_c1_rp'])
        row['first_country'] = parse_first_country(row['countrys_c1_rp'])

        row['ecoom_categorys'] = parse_ecoom_categorys(row)
        row['tags'] = parse_tags(row)
        row['cr_dois'] = parse_cr_dois(row)

        row['c1_address_info'] = parse_address_info(row.get('C1', ''))
        row['orcid_info'] = parse_orcid_info(row.get('OI', ''))
        row['rid_info'] = parse_rid_info(row.get('RI', ''))

        add_row_type(row)
