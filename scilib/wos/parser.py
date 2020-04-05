# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function, division

from .parse_common import parse_is_article, parse_is_oa
from .parse_categorys import parse_ecoom_categorys
from .parse_country import parse_country
from .parse_doi import parse_cr_dois
from .parse_tags import parse_tags


def parse_version1(items):
    """ version1
    """

    for row in items:
        row['parse_version'] = 1

        row['is_article'] = parse_is_article(row)
        row['is_oa'] = parse_is_oa(row)
        row['ecoom_categorys'] = parse_ecoom_categorys(row)

        row['countrys_c1'] = parse_country(row, field='C1', hmt=True)
        row['countrys_rp'] = parse_country(row, field='RP', hmt=True)
        row['countrys_c1_rp'] = parse_country(row, field='C1', extra_field='RP', hmt=True)
        row['cr_dois'] = parse_cr_dois(row)
        row['tags'] = parse_tags(row)
