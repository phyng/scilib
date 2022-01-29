# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function, division

import pandas as pd

PUT_TO_EXCEL_START = 'PUT_TO_EXCEL_START'
PUT_TO_EXCEL_END = 'PUT_TO_EXCEL_END'


def _line_to_dict(line):
    blocks = line.split(' | ')
    column_map = {}
    for index, block in enumerate(blocks):
        if block.strip() == '|':
            continue
        for index2, token in enumerate([i.strip() for i in block.strip().split() if i.strip()]):
            column_map[f'{index}_{index2}'] = token
    return column_map


def _lines_to_table(lines):
    state = None
    headers = []
    bodys = []
    for line in lines:
        if state is None:
            if bodys:
                break
            if line.startswith('------'):
                state = 'HEADER'
            else:
                continue
        elif state == 'HEADER':
            if line.startswith('------'):
                state = 'BODY'
            else:
                headers.append(line)
        elif state == 'BODY':
            if line.startswith('------'):
                state = None
            else:
                bodys.append(line)

    last_header = headers[-1]
    items = [_line_to_dict(last_header)]
    items.extend([_line_to_dict(line) for line in bodys])
    items = [i for i in items if i]
    return items


def put_to_excel(output_log, excel_path):
    lines = output_log.split('\n')

    groups = {}
    state = None
    current_group = None
    for line in lines:
        if state is None:
            if PUT_TO_EXCEL_START in line:
                state = 'IN'
                current_group = [t for t in line.split() if t.startswith(PUT_TO_EXCEL_START)][0]
            else:
                continue
        elif state == 'IN':
            if PUT_TO_EXCEL_END in line:
                state = None
                current_group = None
            else:
                groups.setdefault(current_group, []).append(line)

    all_items = []
    for current_group, lines in groups.items():
        all_items.append(dict(group=current_group.replace(PUT_TO_EXCEL_START, '')))
        all_items.extend(_lines_to_table(lines))
        all_items.append({})
        all_items.append({})

    df = pd.DataFrame.from_records(all_items)
    df.to_excel(excel_path, index=False)
