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


def _pstest_lines_to_table(lines):
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


def _psmatch_lines_to_table(lines):
    state = None
    bodys = []
    for line in lines:
        if state is None:
            if line.startswith('------') and '+' in line:
                state = 'BODY'
            else:
                continue
        elif state == 'BODY':
            if line.startswith('------'):
                state = None
            else:
                bodys.append(line)

    items = []
    items.extend([_line_to_dict(line) for line in bodys])
    items = [i for i in items if i]
    return items


def _get_pstest_rows_summary(rows):
    m_rows = [row for row in rows if row['0_0'] == 'M']
    m_rows_bias_allow = [row for row in m_rows if abs(float(row['1_2'])) <= 10]
    m_rows_bias_not_allow = [row for row in m_rows if abs(float(row['1_2'])) > 10]
    m_rows_p_allow = [row for row in m_rows if abs(float(row['2_1'])) >= 0.01]
    m_rows_p_not_allow = [row for row in m_rows if abs(float(row['2_1'])) < 0.01]
    return dict(
        bias_allow=len(m_rows_bias_allow),
        p_allow=len(m_rows_p_allow),
        bias_not_allow=len(m_rows_bias_not_allow),
        p_not_allow=len(m_rows_p_not_allow),
    )


def put_psmatch_to_excel(output_log, excel_path):
    lines = output_log.split('\n')

    groups = {}
    state = None
    current_group = None
    for line in lines:
        if state is None:
            if line.startswith('. psmatch2'):
                state = 'IN'
                current_group = line
            else:
                continue
        elif state == 'IN':
            if line.startswith('. '):
                state = None
                current_group = None
            else:
                groups.setdefault(current_group, []).append(line)

    all_items = []
    for current_group, lines in groups.items():
        rows = _psmatch_lines_to_table(lines)
        all_items.append({'group': current_group, '0_0': None, '0_1': None})
        all_items.extend([{**row, 'group': current_group} for row in rows])
        all_items.append({})
        all_items.append({})

    df = pd.DataFrame.from_records(all_items)
    df.to_excel(excel_path, index=False)


def put_to_excel(output_log, excel_path, psmatch_output_path):
    put_psmatch_to_excel(output_log, psmatch_output_path)

    lines = output_log.split('\n')

    groups = {}
    state = None
    current_group = None
    for line in lines:
        if state is None:
            if PUT_TO_EXCEL_START in line:
                state = 'IN'
                current_group = [t for t in line.split() if t.startswith(PUT_TO_EXCEL_START)][0]
                current_group = current_group.replace(PUT_TO_EXCEL_START, '').replace(':', '')
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
        rows = _pstest_lines_to_table(lines)
        all_items.append(dict(group=current_group))
        all_items.extend([{**row, 'group': current_group} for row in rows])
        try:
            all_items.append({**_get_pstest_rows_summary(rows), 'group': current_group})
        except (ValueError, KeyError):
            all_items.append(dict(group=current_group + ' summary error'))
        all_items.append({})
        all_items.append({})

    df = pd.DataFrame.from_records(all_items)
    df.to_excel(excel_path, index=False)
