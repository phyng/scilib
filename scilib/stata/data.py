# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function, division

import os
import numpy as np
import pandas as pd
import logging

logger = logging.getLogger('stata')


def use_data_actions(df, actions, working_dir=None):
    for action in actions:
        if action['type'] == 'select':
            df = df[action['columns']]
            logger.info(f'use_data_config df: action={action["type"]} shape={df.shape}')
        elif action['type'] == 'filter_by_contains':
            df = df[df[action['field']].str.contains(action['value'])]
            logger.info(f'use_data_config df: action={action["type"]} shape={df.shape}')
        elif action['type'] == 'extend_by_field':
            _items = []
            for _, row in df.iterrows():
                value = row[action['field']]
                extend_values = [i.strip() for i in str(value).split(',') if i.strip() and i.strip() != 'nan']
                for v in extend_values:
                    _items.append({
                        **row,
                        action['new_field']: v
                    })
            df = pd.DataFrame.from_records(_items)
            logger.info(f'use_data_config df: action={action["type"]} shape={df.shape}')
        elif action['type'] == 'filter_by_value':
            df = df[df[action['field']] == action['value']]
            logger.info(f'use_data_config df: action={action["type"]} shape={df.shape}')
        elif action['type'] == 'filter':
            if action['filter_type'] == '>':
                df = df[df[action['field']] > action['value']]
            elif action['filter_type'] == '>=':
                df = df[df[action['field']] >= action['value']]
            elif action['filter_type'] == '<':
                df = df[df[action['field']] < action['value']]
            elif action['filter_type'] == '<=':
                df = df[df[action['field']] <= action['value']]
            elif action['filter_type'] == '=':
                df = df[df[action['field']] == action['value']]
            else:
                raise ValueError(action['filter_type'])
            logger.info(f'use_data_config df: action={action["type"]} shape={df.shape}')
        elif action['type'] == 'rename':
            df = df.rename(columns={**{k: k for k in df.columns}, **action['columns_map']})
            logger.info(f'use_data_config df: action={action["type"]} shape={df.shape}')
        elif action['type'] == 'dropna':
            df = df.dropna(subset=action['columns'])
            logger.info(f'use_data_config df: action={action["type"]} shape={df.shape}')
        elif action['type'] == 'map_true_false':
            df.replace({False: 0, True: 1}, inplace=True)
            logger.info(f'use_data_config df: action={action["type"]} shape={df.shape}')
        elif action['type'] == 'map_value':
            df[action['field']] = df[action['field']].replace(action['values_map'])
        elif action['type'] == 'create_by_apply':

            def _test(condition, value):
                if condition[0] == '>':
                    return value > condition[1]
                elif condition[0] == '>=':
                    return value >= condition[1]
                elif condition[0] == '<':
                    return value < condition[1]
                elif condition[0] == '<=':
                    return value <= condition[1]
                elif condition[0] == '=':
                    return value == condition[1]
                else:
                    return False

            def _f(row):
                value = row[action['field']]
                for target, conditions in action['values_map'].items():
                    if all(_test(condition, value) for condition in conditions):
                        return target
                return action.get('value_default', value)

            df[action['new_field']] = df.apply(_f, axis=1)

        elif action['type'] == 'df.apply.column_percent':
            _sum = df[action['field']].sum()
            df[action['new_field']] = df[action['field']].apply(lambda x: x / _sum)

        elif action['type'] == 'pd.pivot_table':
            params = action['params']
            _table = pd.pivot_table(
                df[action['fields']],
                values=params.get('values'),
                index=params.get('index'),
                columns=params.get('columns'),
                aggfunc={
                    'count': len,
                    'sum': np.sum,
                    'mean': np.mean,
                }.get(params.get('aggfunc'), len),
            )
            if action.get("actions"):
                _table = use_data_actions(_table, action['actions'], working_dir)
            if working_dir:
                _table.to_csv(os.path.join(working_dir, action['output']))
            return _table

    return df


def use_data_config(data, working_dir):
    df = pd.read_csv(data['from'], low_memory=False)
    logger.info(f'use_data_config df: start shape={df.shape}')

    df = use_data_actions(df, data['actions'], working_dir)
    df.to_csv(os.path.join(working_dir, 'use-data.csv'), index=False)
    return df
