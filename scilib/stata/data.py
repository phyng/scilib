# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function, division

import os
import pandas as pd
import logging

logger = logging.getLogger('stata')


def use_data_config(data, working_dir):
    df = pd.read_csv(data['from'], low_memory=False)
    logger.info(f'use_data_config df: start shape={df.shape}')
    for action in data.get('actions', []):
        if action['type'] == 'select':
            df = df[action['columns']]
            logger.info(f'use_data_config df: action={action["type"]} shape={df.shape}')
        elif action['type'] == 'filter_by_contains':
            df = df[df[action['field']].str.contains(action['value'])]
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

    df.to_csv(os.path.join(working_dir, 'use-data.csv'), index=False)
    df.to_stata(os.path.join(working_dir, 'use-data.dta'), write_index=False)
