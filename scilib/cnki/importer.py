# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function, division

import os
import re
import json
import asyncio
import datetime
import concurrent
from pathlib import Path
from collections import Counter
from pyquery import PyQuery
from libs.iterlib import uniqify

FIELDS = [
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


def parse_fu_tokens(row):
    if row.get('Fund', '') and str(row['Fund']) != 'nan':
        tokens = [re.sub(r'[^a-zA-Z0-9]', '', i) for i in re.split(r'[^a-zA-Z0-9]', row['Fund'])]
        return list(uniqify([i for i in tokens if i]))
    return []


def parse_clc_tokens(row):
    if row.get('CLC', '') and str(row['CLC']) != 'nan':
        clc = row['CLC']
        try:
            clc = clc[:clc.index('ISSN')]
        except ValueError:
            pass
        return [i.strip() for i in clc.split(';') if i.strip()]
    return []


def parse_txt_file(file_path):
    """ 解析自定义导出文件
    """
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
        elif [i for i in FIELDS if line.startswith(i + '-') and not line.startswith('Fund-ing')]:
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


def _parse_list_date(list_date):
    try:
        list_date = list_date.split()[0]
        tokens = list_date.split('-')
        y = int(tokens[0])
        m = int(tokens[1])
        d = int(tokens[2])
        return datetime.date(y, m, d).strftime(r'%Y-%m-%d')
    except Exception:
        return None


def read_spider_format(file_path, fields=None):
    print('file_path', file_path)
    base_dir = os.path.dirname(file_path)
    files = os.listdir(base_dir)
    txt_file = [i for i in files if i.endswith('.txt')][0]
    htmls_file = [i for i in files if i.endswith('.json')][0]

    with open(os.path.join(base_dir, htmls_file)) as f:
        htmls = json.load(f)['htmls']

    raw_txt_items = parse_txt_file(os.path.join(base_dir, txt_file))
    raw_list_items = []
    for html in htmls:
        for row in PyQuery(html).find('tr'):
            pq_row = PyQuery(row)
            list_name = pq_row.find('.name a').text().strip()
            if not list_name:
                continue
            list_marktip = pq_row.find('.name .marktip').text().strip()
            list_author = pq_row.find('.author').text().strip()
            list_source = pq_row.find('.source').text().strip()
            list_date = pq_row.find('.date').text().strip()
            list_data = pq_row.find('.data').text().strip()

            try:
                list_quote = int(pq_row.find('.quote').text().strip() or 0)
                list_download = int(pq_row.find('.download').text().strip() or 0)
            except (ValueError, TypeError):
                continue
            # print(
            #     f'list_name={list_name} list_marktip={list_marktip} list_author={list_author}'
            #     f'list_source={list_source} list_date={list_date} list_data={list_data}'
            #     f'list_quote={list_quote} list_download={list_download}'
            # )

            icon_collect = pq_row.find('.icon-collect')[0]
            list_dbname = icon_collect.attrib['data-dbname']
            list_filename = icon_collect.attrib['data-filename']
            list_id = f'dbname={list_dbname}&filename={list_filename}'

            list_date_format = _parse_list_date(list_date)
            if not list_date_format:
                print('list_date_format error:', list_date, list_date_format)

            list_item = dict(
                list_name=list_name,
                list_marktip=list_marktip,
                list_author=list_author,
                list_source=list_source,
                list_date=list_date,
                list_date_format=list_date_format,
                list_data=list_data,
                list_quote=list_quote,
                list_download=list_download,
                list_dbname=list_dbname,
                list_filename=list_filename,
                list_id=list_id,
            )
            raw_list_items.append(list_item)

    list_items = []
    items = []

    for list_item in raw_list_items:
        # 名称完全匹配
        _match_items = [i for i in raw_txt_items if i.get('Title', '') == list_item['list_name']]
        if len(_match_items) == 1:
            list_item['match_type'] = 'title'
            list_items.append(list_item)
            items.append(_match_items[0])
            continue

        # 中文名称完全匹配且机构完全匹配
        _clean = lambda x: re.sub(r'[^\u4e00-\u9fa5]', '', x)
        _clean_list_name = _clean(list_item['list_name'])
        if len(_clean_list_name) > 5:
            _match_items = [
                i for i in raw_txt_items
                if _clean_list_name == _clean(i.get('Title', '')) and list_item['list_source'] == i.get('Source')
            ]
            if len(_match_items) == 1:
                list_item['match_type'] = 'title_cn'
                list_items.append(list_item)
                items.append(_match_items[0])
                continue

        # 英文名称完全匹配且机构完全匹配
        _clean = lambda x: re.sub(r'[^a-zA-Z]', '', x).lower()
        _clean_list_name = _clean(list_item['list_name'])
        if len(_clean_list_name) > 10:
            _match_items = [
                i for i in raw_txt_items
                if _clean_list_name == _clean(i.get('Title', '')) and list_item['list_source'] == i.get('Source')
            ]
            if len(_match_items) == 1:
                list_item['match_type'] = 'title_en'
                list_items.append(list_item)
                items.append(_match_items[0])
                continue

        # 使用期刊和发表日期
        if list_item['list_source'] and list_item['list_date_format']:
            list_token = str(list_item['list_source']) + ':' + str(list_item['list_date_format'])
            get_item_token = lambda x: str(x.get('Source')) + ':' + str(x.get('PubTime'))[:10]
            _match_items = [
                i for i in raw_txt_items
                if get_item_token(i) == list_token
            ]
            if len(_match_items) == 1:
                list_item['match_type'] = 'source_date'
                list_items.append(list_item)
                items.append(_match_items[0])
                continue

        print('no match', list_item['list_name'])
        list_item['match_type'] = 'no'
        list_items.append(list_item)
        items.append({})

    for item, list_item in zip(items, list_items):
        item.update(list_item)

    for item in items:
        if item.get('Fund'):
            item['fu_tokens'] = parse_fu_tokens(item)
        if item.get('CLC'):
            item['clc_tokens'] = parse_clc_tokens(item)

    if fields:
        for item in items:
            yield {field: item.get(field) for field in fields}
    else:
        yield from iter(items)


def read_spider_format_dir(from_dir, fields=None):
    for file in Path(from_dir).glob('**/end'):
        yield from read_spider_format(file, fields=fields)


async def read_spider_format_dir_parallel(from_dir, callback, *args):
    """ parallel read
    """
    loop = asyncio.get_running_loop()
    futures = []
    with concurrent.futures.ProcessPoolExecutor() as pool:
        for file_path in Path(from_dir).glob('**/end'):
            future = loop.run_in_executor(pool, callback, file_path, *args)
            futures.append(future)
    return await asyncio.gather(*futures, return_exceptions=False)


def collect_keywords(items, keyword_field='Keyword', year_field='Year', keyword_replace_map=None, top_size=50):
    """ 搜集关键词
    """

    keyword_replace_map = keyword_replace_map or {}
    keywords = []
    keywords_map = {}
    tokens_list = []
    for item in items:
        keyword = item.get(keyword_field, '') or ''
        year = item.get(year_field, '') or ''
        if str(keyword) == 'nan' or str(year) == 'nan' or len(str(int(year))) != 4:
            continue
        tokens = re.split(r'[,;，]', keyword)
        tokens = list(set([keyword_replace_map.get(i.strip(), i.strip()) for i in tokens if i and i.strip()]))
        keywords.extend(tokens)
        keywords_map.setdefault(year, []).extend(tokens)
        tokens_list.append((year, tokens))
    counter = Counter(keywords)
    counter_map = {k: Counter(v) for k, v in keywords_map.items()}

    top_n = [k for k, v in counter.most_common(top_size)]
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
            if (index + 1) == top_size:
                print(str(count), end='')
            else:
                print(str(count) + ',', end='')
        print('')

    return counter, counter_map, years_items_flat, corrs
