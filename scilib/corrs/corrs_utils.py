# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function, division
from collections import Counter


def get_corrs(tokens_list, top_size=50):
    counter = Counter([token for tokens in tokens_list for token in tokens])
    top_n = [token for token, _ in counter.most_common(top_size)]

    corrs = []
    for token1 in top_n:
        line = [token1]
        for token2 in top_n:
            count = len([True for tokens in tokens_list if token1 in tokens and token2 in tokens])
            line.append(count)
        corrs.append(line)
    return [counter, corrs]


def corrs_to_csv_string(corrs, name_map=None):
    name_map = name_map or (lambda x: x)
    lines = []
    for row in corrs:
        lines.append(','.join([name_map(row[0])] + [str(i) for i in row[1:]]))
    return '\n'.join(lines)


def corrs_to_cortext_network(corrs, header=None, name_map=None):
    header = header or ['keyword1', 'keyword2']
    name_map = name_map or (lambda x: x)
    items = [header]
    names = [name_map(line[0]) for line in corrs]
    for names1, line in zip(names, corrs):
        for names2, count in zip(names, line[1:]):
            items.extend([[names1, names2] for _ in range(count)])
    return items


def merge_year_cortext_networks(networks, header=None):
    header = header or ['year', 'keyword1', 'keyword2']
    items = [header]
    for year, network in networks.items():
        items.extend([[str(year)] + item for item in network[1:]])
    return items


def cortext_network_to_csv_string(items):
    return '\n'.join([','.join(item) for item in items])
