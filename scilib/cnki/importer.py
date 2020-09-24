# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function, division

import re
from pathlib import Path
from collections import Counter

fields = [
    'SrcDatabase',
    'Title',
    'Author',
    'Organ',
    'Source',
    'Keyword',
    'Summary',
    'PubTime',
    'FirstDuty',
    'Fund',
    'Year',
    'Volume',
    'Period',
    'PageCount',
    'CLC',
]


def parse_txt_file(file_path):
    with open(file_path) as f:
        content = f.read()

    articles = {}
    currentIndex = 0
    currentField = None
    for line in content.split('\n'):
        if line.startswith('SrcDatabase-'):
            currentField = 'SrcDatabase'
            content = line[(line.index(':') + 1):].strip()
            article = articles.setdefault(currentIndex, {})
            if article:
                currentIndex += 1
                article = articles.setdefault(currentIndex, {})
                article[currentField] = article.get(currentField, '') + content
            else:
                article[currentField] = article.get(currentField, '') + content
        elif [i for i in fields if line.startswith(i + '-')]:
            currentField = line.split('-')[0]
            content = line[(line.index(':') + 1):].strip()
            article = articles.setdefault(currentIndex, {})
            article[currentField] = article.get(currentField, '') + content
        else:
            content = line
            article = articles.setdefault(currentIndex, {})
            article[currentField] = article.get(currentField, '') + content
    return articles.values()


def read_text_format_dir(from_dir):
    for file in Path(from_dir).glob('**/*.txt'):
        yield from parse_txt_file(file)


def collect_keywords(items, keyword_replace_map=None):
    keyword_replace_map = keyword_replace_map or {}
    keywords = []
    keywords_map = {}
    tokens_list = []
    for item in items:
        keyword = item.get('Keyword', '') or ''
        year = item.get('Year', '') or ''
        if str(keyword) == 'nan' or str(year) == 'nan' or len(str(int(year))) != 4:
            continue
        tokens = re.split(r'[,;，]', keyword)
        tokens = list(set([keyword_replace_map.get(i.strip(), i.strip()) for i in tokens if i and i.strip()]))
        keywords.extend(tokens)
        keywords_map.setdefault(year, []).extend(tokens)
        tokens_list.append((year, tokens))
    counter = Counter(keywords)
    counter_map = {k: Counter(v) for k, v in keywords_map.items()}

    top_n = [k for k, v in counter.most_common(50)]
    print(top_n)
    years_items = []
    years_items_flat = []
    for year, year_keywords in keywords_map.items():
        years_items_flat.extend([dict(year=year, keyword=k) for k in year_keywords if k in top_n])
        for keyword in top_n:
            if keyword in year_keywords:
                years_items.append([f'{int(year)}', year_keywords.count(keyword), keyword])
    print(years_items)

    corrs = []
    for keyword1 in top_n:
        print(keyword1 + ',', end='')
        for index, keyword2 in enumerate(top_n):
            count = len([True for year, tokens in tokens_list if keyword1 in tokens and keyword2 in tokens])
            corrs.extend([
                dict(year=year, keyword1=keyword1, keyword2=keyword2)
                for year, tokens in tokens_list if keyword1 in tokens and keyword2 in tokens
            ])
            if (index + 1) == 50:
                print(str(count), end='')
            else:
                print(str(count) + ',', end='')
        print('')

    return counter, counter_map, years_items_flat, corrs
