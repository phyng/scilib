# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function, division

from .parse_categorys import SSH_CATEGORYS_SET


def parse_tags(row):
    """ tags

    require:
        - is_article
        - countrys_c1_rp
        - ecoom_categorys
    """

    tags = []
    country_tag_map = {
        'china': 'mainland_article',
        'hong kong': 'hk_article',
        'macao': 'macao_article',
        'taiwan': 'taiwan_article',
        'usa': 'usa_article',
        'japan': 'japan_article',
        'uk': 'uk_article',
    }

    for key, value in country_tag_map.items():
        if row['is_article'] and key in row['countrys_c1_rp']:
            tags.append(value)

    ecoom_categorys = [i.strip().lower() for i in str(row['ecoom_categorys']).split(';')]
    if SSH_CATEGORYS_SET & set(ecoom_categorys):
        tags.append('ecoom7')

    return ';'.join(tags)
