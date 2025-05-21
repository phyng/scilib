# coding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import asyncio
import json
import os
import re
from pathlib import Path
from pyquery import PyQuery
from concurrent.futures import ProcessPoolExecutor

from .parser import CNKI_FIELDS, get_clc_map, parse_cnki_item, parse_list_date


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
        elif [i for i in CNKI_FIELDS if line.startswith(i + '-') and not line.startswith('Fund-ing')]:
            currentField = line.split('-')[0]
            content = line[(line.index(':') + 1):].strip()
            article = articles.setdefault(currentIndex, {})
            article[currentField] = article.get(currentField, '') + content
        else:
            content = line
            article = articles.setdefault(currentIndex, {})
            article[currentField] = article.get(currentField, '') + content
    return articles.values()


def read_text_format_dir(from_dir, keyword_replace_map=None):
    clc_map = get_clc_map()
    for file in Path(from_dir).glob('**/*.txt'):
        for item in parse_txt_file(file):
            parse_cnki_item(item, clc_map, keyword_replace_map)
            yield item


def read_spider_format(file_path, *, fields=None, keyword_replace_map=None):
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
            list_name = str(pq_row.find('.name a').text()).strip()
            if not list_name:
                continue
            list_marktip = str(pq_row.find('.name .marktip').text()).strip()
            list_author = str(pq_row.find('.author').text()).strip()
            list_source = str(pq_row.find('.source').text()).strip()
            list_date = str(pq_row.find('.date').text()).strip()
            list_data = str(pq_row.find('.data').text()).strip()

            try:
                list_quote = int(str(pq_row.find('.quote').text()).strip() or 0)
                list_download = int(str(pq_row.find('.download').text()).strip() or 0)
            except (ValueError, TypeError):
                continue
            # print(
            #     f'list_name={list_name} list_marktip={list_marktip} list_author={list_author}'
            #     f'list_source={list_source} list_date={list_date} list_data={list_data}'
            #     f'list_quote={list_quote} list_download={list_download}'
            # )

            if not pq_row.find('.icon-collect'):
                continue

            icon_collect = pq_row.find('.icon-collect')[0]
            list_dbname = icon_collect.attrib['data-dbname']
            list_filename = icon_collect.attrib['data-filename']
            list_id = f'dbname={list_dbname}&filename={list_filename}'
            list_date_format = parse_list_date(list_date)
            # if not list_date_format:
            #     print('list_date_format error:', list_date, list_date_format)

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
        _clean = lambda x: re.sub(r'[^\u4e00-\u9fa5]', '', x)  # noqa: E731
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
        _clean = lambda x: re.sub(r'[^a-zA-Z]', '', x).lower()  # noqa: E731
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
            get_item_token = lambda x: str(x.get('Source')) + ':' + str(x.get('PubTime'))[:10]  # noqa: E731
            _match_items = [
                i for i in raw_txt_items
                if get_item_token(i) == list_token
            ]
            if len(_match_items) == 1:
                list_item['match_type'] = 'source_date'
                list_items.append(list_item)
                items.append(_match_items[0])
                continue

        # print('no match', list_item['list_name'])
        list_item['match_type'] = 'no'
        list_items.append(list_item)
        items.append({})

    for item, list_item in zip(items, list_items):
        item.update(list_item)

    clc_map = get_clc_map()
    for item in items:
        parse_cnki_item(item, clc_map, keyword_replace_map)

    if fields:
        for item in items:
            yield {field: item.get(field) for field in fields}
    else:
        yield from iter(items)


def read_spider_format_dir(from_dir, fields=None, *, keyword_replace_map=None):
    for file in Path(from_dir).glob('**/end'):
        yield from read_spider_format(file, fields=fields, keyword_replace_map=keyword_replace_map)


async def read_spider_format_dir_parallel(from_dir, callback, *args):
    """ parallel read
    """
    loop = asyncio.get_running_loop()
    futures = []
    with ProcessPoolExecutor() as pool:
        for file_path in Path(from_dir).glob('**/end'):
            future = loop.run_in_executor(pool, callback, file_path, *args)
            futures.append(future)
    return await asyncio.gather(*futures, return_exceptions=False)
