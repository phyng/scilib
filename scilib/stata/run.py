# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function, division

import os
import json
import time
import subprocess
from pathlib import Path
import logging
import traceback
import pandas as pd

from .base import call, call_batch
from .plugin import start_with_cd, xls2dta
from .put import put_to_excel
from .data import use_data_config
from .action import use_actions

logging.basicConfig(
    format='%(asctime)s,%(msecs)d %(levelname)s %(name)s [%(filename)s:%(lineno)d] %(message)s',
    datefmt=r'%Y-%m-%d:%H:%M:%S',
    level=logging.DEBUG,
    filename=os.environ.get('LOG_FILE'),
    filemode='a',
)

STATA_ENTRY = os.environ.get('STATA_ENTRY', '/Applications/Stata/StataMP.app/Contents/MacOS/StataMP')
logger = logging.getLogger('stata')
logger.addHandler(logging.StreamHandler())


def run(working_dir):
    """ https://www.stata.com/support/faqs/mac/advanced-topics/
    """
    with open(os.path.join(working_dir, 'config.json')) as f:
        config = json.load(f)

    actions = [
        start_with_cd(working_dir),
    ]

    if config.get('data'):
        df = use_data_config(config['data'], working_dir)
        if config.get('actions'):
            df.to_stata(os.path.join(working_dir, 'use-data.dta'), write_index=False)
            actions.append(call('use "use-data.dta"'))
        else:
            with open(os.path.join(working_dir, 'run.end'), 'w') as f:
                f.write('success')
            return

    if os.path.exists(os.path.join(working_dir, 'use-data.xlsx')):
        actions.append(xls2dta('use-data.xlsx', 'use-data.dta'))

    use_actions(actions, config['actions'])

    do_content = call_batch(*actions)
    do_file = os.path.join(working_dir, 'run.do')
    with open(do_file, 'w') as f:
        f.write(do_content)

    try:
        subprocess.call([
            STATA_ENTRY,
            '-b',
            '-e',
            'do',
            'run.do'
        ], cwd=working_dir, timeout=5 * 60)
        with open(os.path.join(working_dir, 'run.end'), 'w') as f:
            f.write('success')
        run_log = os.path.join(working_dir, 'run.log')
        if os.path.exists(run_log):
            with open(run_log, 'r') as f:
                put_to_excel(
                    f.read(),
                    os.path.join(working_dir, 'output.xlsx'),
                    os.path.join(working_dir, 'psmatch_output.xlsx'),
                )

    except subprocess.TimeoutExpired:
        logger.error(f'执行超时 {working_dir} subprocess.TimeoutExpired')
        with open(os.path.join(working_dir, 'run.end'), 'w') as f:
            f.write('error')


def run_all(entry_dir):
    for file in Path(entry_dir).glob('**/config.json'):
        working_dir = os.path.dirname(file)
        if not (os.path.isdir(working_dir)):
            continue
        run_end = os.path.join(working_dir, 'run.end')
        if os.path.exists(run_end):
            continue

        running = os.path.join(working_dir, 'running.txt')
        if os.path.exists(running):
            continue

        try:
            with open(running, 'w') as f:
                f.write('')
            logger.info(f'正在执行 {working_dir}...')
            run(working_dir)
        except Exception as e:
            logger.error(f'执行失败 {working_dir} {e}')
            with open(os.path.join(working_dir, 'run.end'), 'w') as f:
                f.write(traceback.format_exc())
        finally:
            if os.path.exists(running):
                os.remove(running)


def run_summary(entry_dir):
    summary_rows = []
    for file in Path(entry_dir).glob('**/config.json'):
        working_dir = os.path.dirname(file)
        working_dir_rel = os.path.relpath(working_dir, entry_dir)
        if not (os.path.isdir(working_dir)):
            continue
        logger.info(f'开始执行 {working_dir}...')
        config_row = {'working_dir': working_dir_rel, 'type': 'config', 'state': '未执行'}
        summary_rows.append(config_row)

        run_end = os.path.join(working_dir, 'run.end')
        if not os.path.exists(run_end):
            logger.info(f'忽略未完成文件夹 {working_dir}')
            continue
        else:
            config_row['state'] = '已执行'

        with open(os.path.join(working_dir, 'config.json')) as f:
            config = json.load(f)

        run_log = os.path.join(working_dir, 'run.log')
        if os.path.exists(run_log):
            with open(run_log, 'r') as f:
                put_to_excel(
                    f.read(),
                    os.path.join(working_dir, 'output.xlsx'),
                    os.path.join(working_dir, 'psmatch_output.xlsx'),
                )

        for action in config['actions']:
            if action['type'] == 'psm':
                pws_row = {f'psm_{k}': v for k, v in action.items()}
                output_excel = os.path.join(working_dir, 'output.xlsx')
                if not os.path.exists(output_excel):
                    continue
                df_output = pd.read_excel(output_excel, engine="openpyxl")
                try:
                    df_output.dropna(subset=['bias_allow', 'p_allow', 'bias_not_allow', 'p_not_allow'], inplace=True)
                except KeyError:
                    continue
                df_output.dropna(axis=1, inplace=True)
                for _, ptest_row in df_output.iterrows():
                    summary_rows.append({
                        'working_dir': working_dir_rel,
                        'type': 'psm',
                        'state': '已执行',
                        **pws_row,
                        **ptest_row
                    })

    df_summary = pd.DataFrame.from_records(summary_rows)
    df_summary.to_excel(os.path.join(entry_dir, 'summary.xlsx'), index=False)


if __name__ == '__main__':
    if os.environ.get('ACTION') == 'summary':
        run_summary(os.environ['DIR_AUTOPROCESS'])
    elif os.environ.get('ACTION') == 'watch_summary':
        while True:
            run_summary(os.environ['DIR_AUTOPROCESS'])
            time.sleep(30)
    elif os.environ.get('ACTION') == 'watch':
        while True:
            run_all(os.environ['DIR_AUTOPROCESS'])
            time.sleep(10)
    else:
        run_all(os.environ['DIR_AUTOPROCESS'])
