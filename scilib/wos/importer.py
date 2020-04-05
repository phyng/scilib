# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function, division

import pandas as pd
from pathlib import Path


def _read_text_format_lines(lines):
    items = []
    current_item = None
    current_item_key = None
    for index, line in enumerate(lines):
        if line.startswith('null') and line.endswith('null'):
            continue
        start = line[:2]
        end = line[3:]
        if start in ['FN', 'VR', 'EF']:
            continue
        elif start == 'PT' or 'nullPT' in line:
            current_item = {}
            current_item[start] = [end]
            current_item_key = start
        elif start == '  ':
            if current_item and current_item_key:
                current_item[current_item_key].append(end)
        elif start == 'ER':
            items.append(current_item)
            current_item = None
            current_item_key = None
        elif len(start) == 2:
            if current_item is None:
                print('[WARN] _read_text_format_lines', index, line)
            current_item[start] = [end]
            current_item_key = start
        else:
            continue
    return items


def read_text_format_dir(abs_path, globs=None):
    globs = globs or ['**/*.txt', '**/*.csv', '*.csv', '*.txt']
    for glob in globs:
        for path in Path(abs_path).glob(glob):
            with open(path, 'r', encoding='utf-8-sig') as f:
                lines = f.read().split('\n')
            try:
                items = _read_text_format_lines(lines)
            except Exception:
                print('[WARN] read_text_format_dir', path)
                raise
            for item in items:
                data = {}
                for k, v in item.items():
                    if k in ['WC', 'SC']:
                        data[k] = ' '.join(v)
                    else:
                        data[k] = '; '.join(v)
                yield data


def read_text_format_dir_as_pd(abs_path, globs=None):
    all_items = read_text_format_dir(abs_path, globs)
    return pd.DataFrame.from_records(all_items).drop_duplicates('UT')
