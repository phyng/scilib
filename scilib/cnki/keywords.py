# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function, division

from collections import Counter
from functools import partial
from .importer import parse_keyword_tokens, parse_year


def collect_keywords(
    items,
    *,
    keyword_field='Keyword',
    keyword_replace_map=None,
    keyword_func=None,
    top_size=50
):
    """ collect keywords corrs and counter
    """
    keyword_func = keyword_func or partial(
        parse_keyword_tokens, keyword_field=keyword_field, keyword_replace_map=keyword_replace_map
    )
    keywords = []
    year_keywords = {}
    tokens_list = []
    for item in items:
        tokens = keyword_func(item)
        if tokens is None:
            continue

        year = parse_year(item)
        if not year:
            continue

        keywords.extend(tokens)
        year_keywords.setdefault(year, []).extend(tokens)
        tokens_list.append(tokens)

    counter = Counter(keywords)
    year_counters = {year: Counter(tokens) for year, tokens in year_keywords.items()}
    top_n = [k for k, v in counter.most_common(top_size)]

    corrs = []
    for keyword1 in top_n:
        line = [keyword1]
        for keyword2 in top_n:
            count = len([True for tokens in tokens_list if keyword1 in tokens and keyword2 in tokens])
            line.append(count)
        corrs.append(line)

    return dict(
        counter=counter,
        year_counters=year_counters,
        corrs=corrs
    )
